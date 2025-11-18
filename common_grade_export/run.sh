#!/bin/bash

# Run from common_grade_export

docker build -t 'grade_exporter:latest' .


SYSTEM_CRED=/tmp/system_cred.json

cat > $SYSTEM_CRED <<EOF
{
    "moodle": "$MOODLE_TOKEN",
    "dis": "$DIS_ACCESS_TOKEN",
    "stepik": {
        "client_id": "$STEPIK_CLIENT_ID",
        "client_secret": "$STEPIK_CLIENT_SECRET"
    }
}
EOF

 
TABLE_ID=$TABLE_ID
SHEET_ID=$SHEET_ID
GOOGLE_CRED=$EXPORTER_GOOGLE_CONF

GOOGLE_CRED_DOCKER_PATH=/app/secret.json
CRED_DOCKER_PATH=/app/system_cred.json

docker run --rm -v $GOOGLE_CRED:$GOOGLE_CRED_DOCKER_PATH -v $SYSTEM_CRED:$CRED_DOCKER_PATH grade_exporter:latest course_to_spreadsheet_exporter.py --table_id $TABLE_ID --sheet_id $SHEET_ID --google_cred $GOOGLE_CRED_DOCKER_PATH --system_cred $CRED_DOCKER_PATH