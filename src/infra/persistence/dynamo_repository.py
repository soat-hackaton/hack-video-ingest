from src.core.interfaces.repositories import VideoRepositoryInterface
from src.core.entities.video_task import VideoTask
from src.infra.aws.session import get_boto_session

class DynamoDBVideoRepo(VideoRepositoryInterface):
    def __init__(self, table_name: str):
        session = get_boto_session()
        self.dynamodb = session.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)

    def save(self, task: VideoTask):
        item = {
            'PK': f"VIDEO#{task.id}",
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
            Key={'PK': f"VIDEO#{task_id}", 'SK': "METADATA"},
            UpdateExpression="set #st = :s",
            ExpressionAttributeNames={'#st': 'status'},
            ExpressionAttributeValues={':s': new_status}
        )