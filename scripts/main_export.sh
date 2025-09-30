#!/bin/bash
# Run from ./scripts
# set envvars: EXPORT_INFO_TABLE_ID, EXPORT_INFO_SHEET_ID, GOOGLE_CONF

source ./export_courses.sh

TABLE_ID=$EXPORT_INFO_TABLE_ID
SHEET_ID=$EXPORT_INFO_SHEET_ID
FILE="export"
GOOGLE_CRED=$EXPORTER_GOOGLE_CONF
FORMAT="csv"

# download table w/export info
python3 download_file.py --table_id "$TABLE_ID" --sheet_id "$SHEET_ID" --google_cred "$GOOGLE_CONF" --format $FORMAT --filename "$FILE"

# read csv to array
while IFS= read -r line 
do
  exports+=("$line")
done < $FILE.$FORMAT

exportCourses "${exports[@]}"