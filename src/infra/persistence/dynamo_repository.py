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