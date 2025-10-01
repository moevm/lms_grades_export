#!/bin/bash

# usage function in other script:
# source ./scripts/duplicate_to_yadisk.sh
# exports=(
#   'humanreadable_subject,table_id,sheet_id,export_format,export_name'
# )
# YADISK_TOKEN=... YADISK_TDIR=... GOOGLE_CRED=... duplicateToYadisk "${exports[@]}"


function duplicateSheetsToYadisk() {
    # get args (=array of csv rows)
    exports=("$@")
    
    # init log file
    log_file="diplicateSheets.log"
    echo "" > $log_file

    # proccess
    for line in "${exports[@]}"; do
        IFS=',' read -r -a current_export <<< "$line"

        info_msg=">>>>> Экспорт для дисциплины ${current_export[0]} из таблицы ${current_export[1]}, лист ${current_export[2]} в ${current_export[4]} (формат ${current_export[3]})"
        echo $info_msg
        echo $info_msg >> $log_file
        
        # export to file
        python3 download_file.py --table_id "${current_export[1]}" --sheet_id "${current_export[2]}" --google_cred "$GOOGLE_CRED" --format ${current_export[3]} --filename "${current_export[4]}" 

        # upload file
        YADISK_TOKEN=$YADISK_TOKEN python3 -c "import yadisk_manager; yadisk_manager.upload_file_to_disk(file_path='${current_export[4]}.${current_export[3]}', abs_disk_path='$YADISK_TDIR')" 
        
        end_info_msg=">>>>> Конец экспорта для дисциплины"
        echo $end_info_msg
        echo $end_info_msg >> $log_file
    done
}

