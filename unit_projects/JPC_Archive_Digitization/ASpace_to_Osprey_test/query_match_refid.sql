with f as (
select distinct SUBSTRING_INDEX(file_name, '_', 1) refid from files where folder_id in (select folder_id from folders where project_id = 186 or project_id = 201))
select distinct f.refid, j.refid from f left join jpc_aspace_data j on f.refid = j.refid