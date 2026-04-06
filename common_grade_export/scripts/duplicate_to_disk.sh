#!/bin/bash

# Run from common_grade_export

docker build -t 'grade_exporter:latest' .


TABLE_ID=$TABLE_ID
SHEET_ID=$SHEET_ID
GOOGLE_CRED=$EXPORTER_GOOGLE_CONF

GOOGLE_CRED_DOCKER_PATH=/app/secret.json

docker run --rm -v $GOOGLE_CRED:$GOOGLE_CRED_DOCKER_PATH grade_exporter:latest spreadsheet_to_yadisk_duplicator.py \
		--table_id $EXPORT_INFO_TABLE_ID --sheet_id $EXPORT_INFO_SHEET_ID --google_cred $GOOGLE_CRED_DOCKER_PATH \
		--yadisk_token $YADISK_TOKEN --yadisk_dir "$YADISK_DIR"