import psycopg2

regions = [
    'aws-0-us-east-1',
    'aws-0-us-west-1',
    'aws-0-us-west-2',
    'aws-0-eu-central-1',
    'aws-0-eu-west-1',
    'aws-0-eu-west-2',
    'aws-0-ap-southeast-1',
    'aws-0-ap-southeast-2',
    'aws-0-ap-northeast-1',
    'aws-0-ap-northeast-2',
    'aws-0-sa-east-1',
    'aws-0-ca-central-1',
    'aws-0-ap-south-1'
]

for region in regions:
    host = f'{region}.pooler.supabase.com'
    print(f'Trying {host}...')
    try:
        conn = psycopg2.connect(
            host=host,
            database='postgres',
            user='postgres.wfkilhwghdkddxgcljyq',
            password='ftcalex4rAOYifLW',
            port=6543,
            connect_timeout=3
        )
        print(f'SUCCESS! Region is: {region}')
        conn.close()
        break
    except Exception as e:
        print(f'Error for {region}: {str(e).strip()}')

