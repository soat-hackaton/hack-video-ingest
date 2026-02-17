import os
from datetime import datetime
from boto3.dynamodb.conditions import Key
from src.infra.api.schemas.upload import TaskStatus
from src.core.interfaces import RepositoryInterface
from src.core.entities.video_task import VideoTask
from src.infra.aws.session import get_boto_session

class DynamoDBVideoRepo(RepositoryInterface):
    def __init__(self):
        session = get_boto_session()
        self.dynamodb = session.resource('dynamodb')
        self.table = self.dynamodb.Table(os.getenv("DYNAMO_TABLE_NAME"))

    def save(self, task: VideoTask):
        item = {
            'PK': task.id,
            'SK': "METADATA",
            'id': task.id,
            'filename': task.filename,
            's3_path': task.s3_path,
            's3_download_path': task.s3_download_path,
            'status': task.status,
            'user_email': task.user_email,
            'created_at': task.created_at.isoformat()
        }
        self.table.put_item(Item=item)

    def update_status(self, task_id: str, new_status: str):
        self.table.update_item(
            Key={'PK': task_id, 'SK': "METADATA"},
            UpdateExpression="set #st = :s",
            ExpressionAttributeNames={'#st': 'status'},
            ExpressionAttributeValues={':s': new_status}
        )

    def find_by_id(self, task_id: str) -> dict:
        response = self.table.get_item(Key={'PK': task_id, 'SK': "METADATA"})
        return response.get('Item')

    def list_by_user(self, user_email: str):
        response = self.table.query(
            IndexName='UserEmailIndex',
            KeyConditionExpression=Key('user_email').eq(user_email)
        )

        # Retornar ordenado pela data de criação
        items = response.get('Items', [])
        items.sort(key=lambda x: x['created_at'], reverse=True)
        return items

    def update_status(
        self, 
        task_id: str, 
        new_status: TaskStatus, 
        s3_download_path: str = None
    ) -> dict:
        # Expressão base
        keys = {
            'PK': task_id,
            'SK': "METADATA"
        },
        update_expr = "SET #st = :s, #updated = :u"
        expr_names = {
            '#st': 'status',
            '#updated': 'updated_at'
        }
        expr_values = {
            ':s': new_status.value if hasattr(new_status, 'ERROR') else new_status,
            ':u': datetime.utcnow().isoformat()
        }

        # Lógica dinâmica: Se vier o caminho, adicionamos ao update
        if s3_download_path:
            update_expr += ", #path = :p"
            expr_names['#path'] = 's3_download_path'
            expr_values[':p'] = s3_download_path

        response = self.table.update_item(
            Key=keys,
            UpdateExpression=update_expr,
            ExpressionAttributeNames=expr_names,
            ExpressionAttributeValues=expr_values,
            ConditionExpression="attribute_exists(PK)",
            ReturnValues="ALL_NEW"
        )

        return response.get("Attributes")