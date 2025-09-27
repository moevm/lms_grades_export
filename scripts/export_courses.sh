#!/bin/bash

# usage function in other script:
# source ./scripts/export_courses.sh
# exports=(
#   'humanreadable_subject,table_id,sheet_name,system,exportinfo'
# )
# system: "moodle" - Предмет,1zG21U9zJHIkfAM5ejd8WBw,Онлайн-курс,moodle,course_id
# system: "stepik" - Предмет,1zG21U9zJHIkfAM5ejd8WBw,Онлайн-курс,stepik,course_id,class_id
# system: "dis" - Предмет,1zG21U9zJHIkfAM5ejd8WBw,Онлайн-курс,dis,filter
# exportCourses "${exports[@]}"


source ./download_file.sh

is_error=0

function exportCourses() {
    # get args (=array of csv rows)
    exports=("$@")
    
    # init log file
    log_file="exportCourses.log"
    echo "" > $log_file

    # proccess
    for line in "${exports[@]}"; do
        IFS=',' read -r -a current_export <<< "$line"

        info_msg=">>>>> Экспорт для дисциплины ${current_export[0]} из ${current_export[3]} в таблицу ${current_export[1]} на лист ${current_export[2]}"
        echo $info_msg
        echo $info_msg >> $log_file
        
          case "${current_export[3]}" in
            "moodle")
                docker run --rm -v $EXPORTER_GOOGLE_CONF:/app/conf.json moodle_export_parser:latest \
                    --moodle_token $MOODLE_TOKEN --url https://e.moevm.info \
                    --csv_path grades --google_token conf.json \
                    --course_id ${current_export[4]} \
                    --table_id ${current_export[1]} \
                    --sheet_name "${current_export[2]}" \
                    --options github >> $log_file

                return_code=$?
                ;;
            "stepik")
                docker run --rm -v $EXPORTER_GOOGLE_CONF:/app/conf.json stepik_export_parser:latest \
                    --client_id $STEPIK_CLIENT_ID --client_secret $STEPIK_CLIENT_SECRET \
                    --url https://stepik.org:443/api \
                    --csv_path grades --google_token conf.json \
                    --course_id ${current_export[4]} \
                    --class_id ${current_export[5]} \
                    --table_id ${current_export[1]} \
                    --sheet_name "${current_export[2]}" >> $log_file

                return_code=$?
                ;;
            "dis")
                docker run --rm -v $EXPORTER_GOOGLE_CONF:/app/conf.json checker_export_parser:latest \
                    --checker_filter "${current_export[4]}" \
                    --checker_token $DIS_ACCESS_TOKEN \
                    --table_id ${current_export[1]} \
                    --sheet_name "${current_export[2]}" >> $log_file

                return_code=$?
                ;;
            *)
                echo "Недопустимое значение: '${current_export[3]}'"
                return_code=1
                ;;
        esac

        if [[ "$return_code" -ne "0" ]]; then
            error_info_msg="!!!!! Возникла ошибка во время экспорта для ${current_export[0]}"
            echo $error_info_msg
            echo $error_info_msg >> $log_file
            cat $log_file
            is_error=1
        fi
        
        end_info_msg=">>>>> Конец экспорта для дисциплины"
        echo $end_info_msg
        echo $end_info_msg >> $log_file
    done

    if [[ "$is_error" -ne "0" ]]; then
        error_info_msg="!!!!! Возникла ошибка во время экспорта - проверьте логи"
        exit 1
    fi

}
