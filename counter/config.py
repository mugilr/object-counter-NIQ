import os

from counter.adapters.count_repo import CountMongoDBRepo, CountInMemoryRepo, CountPostgresRepo
from counter.adapters.object_detector import TFSObjectDetector, FakeObjectDetector
from counter.domain.actions import CountDetectedObjects


def dev_fake_count_action() -> CountDetectedObjects:
    return CountDetectedObjects(FakeObjectDetector(), CountInMemoryRepo())


def prod_mongo_count_action() -> CountDetectedObjects:
    tfs_host = os.environ.get('TFS_HOST', 'tfserving')
    tfs_port = os.environ.get('TFS_PORT', 8501)
    mongo_host = os.environ.get('MONGO_HOST', 'test-mongo')
    mongo_port = os.environ.get('MONGO_PORT', 27017)
    mongo_db = os.environ.get('MONGO_DB', 'prod_counter')
    return CountDetectedObjects(TFSObjectDetector(tfs_host, tfs_port, 'rfcn'),
                                CountMongoDBRepo(host=mongo_host, port=mongo_port, database=mongo_db))

def prod_postgres_count_action() -> CountDetectedObjects:
    tfs_host = os.environ.get('TFS_HOST', 'tfserving')
    tfs_port = os.environ.get('TFS_PORT', 8501)
    pg_host = os.environ.get('PG_HOST', 'postgres')
    pg_port = os.environ.get('PG_PORT', 5432)
    pg_db = os.environ.get('PG_DB', 'tfserving')
    pg_user = os.environ.get('PG_USER', 'postgres')
    pg_password = os.environ.get('PG_PASSWORD', 'postgres')
    return CountDetectedObjects(TFSObjectDetector(tfs_host, tfs_port, 'rfcn'),
                                CountPostgresRepo(host=pg_host, port=pg_port, database=pg_db, username=pg_user, password=pg_password))


def get_count_action() -> CountDetectedObjects:
    env = os.environ.get('ENV', 'dev')
    db_type = os.environ.get('DB_TYPE', 'fake')
    count_action_fn = f"{env}_{db_type}_count_action"
    return globals()[count_action_fn]()
