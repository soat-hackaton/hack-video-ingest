from datetime import datetime
from boto3.dynamodb.conditions import Key
from src.infra.api.schemas.upload import TaskStatus
from src.core.interfaces import RepositoryInterface
from src.core.entities.video_task import VideoTask
from src.infra.aws.session import get_boto_session

class DynamoDBVideoRepo(RepositoryInterface):
    def __init__(self, table_name: str):
        session = get_boto_session()
        self.dynamodb = session.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)

    def save(self, task: VideoTask):
        item = {
            'PK': task.id,
            'SK': "METADATA",
            'id': task.id,
            'filename': task.filename,
            's3_path': task.s3_path,
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

    def update_status(self, task_id: str, new_status: TaskStatus) -> dict:
        response = self.table.update_item(
            Key={
                'PK': task_id,
                'SK': "METADATA"
            },
            UpdateExpression="SET #st = :s, #updated = :u",
            ExpressionAttributeNames={
                '#st': 'status',
                '#updated': 'updated_at'
            },
            ExpressionAttributeValues={
                ':s': new_status.value,
                ':u': datetime.utcnow().isoformat()
            },
            ConditionExpression="attribute_exists(PK)",
            ReturnValues="ALL_NEW"
        )

        return response.get("Attributes")