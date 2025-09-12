select count(*) from file_postprocessing fp where post_step = 'id_manager_arches' and post_results = 0 and file_id in 
(select file_id from files where folder_id in (select folder_id from folders where project_id = 201))
and file_id in (select file_id from files where dams_uan is not null)

select f.* from files f where folder_id in (select folder_id from folders where project_id = 201)
 and f.dams_uan is not null and f.file_id not in (
select file_id from file_postprocessing fp where post_step = 'id_manager_aspace' and post_results = 0 and file_id in 
(select file_id from files where folder_id in (select folder_id from folders where project_id = 201))
and file_id in (select file_id from files where dams_uan is not null)
)







python3 arches_pull.py 10000 10000


select count(*) from file_postprocessing fp where post_step = 'arches_record' and post_results = 0 and file_id in 
(select file_id from files where folder_id in (select folder_id from folders where project_id = 201 ))
and file_id in (select file_id from files where dams_uan is not null)



select f.* from files f where folder_id in (select folder_id from folders where project_id = 201)
 and f.dams_uan is not null and f.file_id not in (
select file_id from file_postprocessing fp where post_step = 'arches_record' and post_results = 0 and file_id in 
(select file_id from files where folder_id in (select folder_id from folders where project_id = 201))
and file_id in (select file_id from files where dams_uan is not null)
)





# Full report

select  
    f.file_name,
    fol.project_folder as folder,
    f.dams_uan,
    concat('https://si-osprey.si.edu/file/', f.file_id) as link_osprey,
    fp1.post_info as id_manager_aspace,
    fp2.post_info as id_manager_arches,
    fp3.post_info as arches_record

from 
    files f
        LEFT JOIN file_postprocessing fp1 ON (f.file_id = fp1.file_id AND fp1.post_step = 'id_manager_aspace')
        LEFT JOIN file_postprocessing fp2 ON (f.file_id = fp2.file_id AND fp2.post_step = 'id_manager_arches')
        LEFT JOIN file_postprocessing fp3 ON (f.file_id = fp3.file_id AND fp3.post_step = 'arches_record'),
    folders fol
where 
    f.folder_id = fol.folder_id 
      AND (fol.project_id = 201)
    AND f.dams_uan is not null 

 
 
 
select file_id from file_postprocessing fp where post_step = 'arches_record' and post_results = 0 and file_id in 
(select file_id from files where folder_id in (select folder_id from folders where project_id = 201))
and file_id in (select file_id from files where dams_uan is not null)
)
