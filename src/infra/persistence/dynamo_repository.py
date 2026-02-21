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

    # def update_status(self, task_id: str, new_status: str):
    #     self.table.update_item(
    #         Key={'PK': task_id, 'SK': "METADATA"},
    #         UpdateExpression="set #st = :s",
    #         ExpressionAttributeNames={'#st': 'status'},
    #         ExpressionAttributeValues={':s': new_status}
    #     )

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

    def count_processing_by_user(self, user_email: str) -> int:
        response = self.table.query(
            IndexName='UserEmailIndex',
            KeyConditionExpression=Key('user_email').eq(user_email)
        )
        
        # Filtra na memória os items com status PROCESSING
        # Note: Idealmente, usar um filter_expression do Dynamo, mas como a volumetria
        # ativa do usuário não é enorme, manter em memória é seguro o suficiente para agora.
        # Caso contrário:
        # FilterExpression=Attr('status').eq('PROCESSING')
        items = response.get('Items', [])
        processing_count = sum(1 for item in items if item.get('status') == TaskStatus.PROCESSING.value)
        return processing_count

    def get_oldest_queued_by_user(self, user_email: str) -> dict | None:
        response = self.table.query(
            IndexName='UserEmailIndex',
            KeyConditionExpression=Key('user_email').eq(user_email)
        )
        
        items = response.get('Items', [])
        
        # Filtrar apenas as tasks no estado QUEUED
        queued_items = [item for item in items if item.get('status') == TaskStatus.QUEUED.value]
        
        if not queued_items:
            return None
            
        # Encontrar e retornar a mais antiga (baseada em created_at)
        oldest_item = min(queued_items, key=lambda x: x['created_at'])
        return oldest_item

    def update_status(
        self, 
        task_id: str, 
        new_status: TaskStatus, 
        s3_download_path: str = None
    ) -> dict:
        keys = {
            'PK': task_id,
            'SK': "METADATA"
        }
        update_expr = "SET #st = :s, #updated = :u"
        expr_names = {
            '#st': 'status',
            '#updated': 'updated_at'
        }
        expr_values = {
            ':s': new_status.value if hasattr(new_status, 'ERROR') else new_status,
            ':u': datetime.utcnow().isoformat()
        }

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