select folder_id from files where dams_uan is not null and folder_id in (select folder_id from folders where project_id = 201) and file_id not in 
(
select f.file_id from files f, folders fol, file_postprocessing fp where (fol.project_id = 201) and f.folder_id = fol.folder_id and 
f.file_id = fp.file_id and fp.post_step = 'id_manager_arches'
)
group by folder_id




select id1_value from jpc_massdigi_ids jmi where jmi.id_relationship = 'refid_hmo' and 
id1_value not in 
(
    select SUBSTRING_INDEX(f.file_name, '_', 1) as refid from files f, folders fol where f.folder_id = fol.folder_id and fol.project_id = 201 and f.dams_uan is not null
)









select count(f.file_id) from files f, file_postprocessing fp where f.folder_id in (select folder_id from folders where project_id = 201) and f.file_id = fp.file_id 
and fp.post_step ='id_manager_arches' and fp.post_results = 0 and fp.post_info like 'https:%'




select count(f.file_id) from files f, file_postprocessing fp where f.folder_id in (select folder_id from folders where project_id = 201) and f.file_id = fp.file_id 
and fp.post_step ='id_manager_aspace' and fp.post_results = 0 and fp.post_info like 'https:%'


select count(f.file_id) from files f, file_postprocessing fp where f.folder_id in (select folder_id from folders where project_id = 201) and f.file_id = fp.file_id 
and fp.post_step ='arches_record' and fp.post_results = 0 and fp.post_info like 'https:%'















select folder_id from folders where project_id = 201 and delivered_to_dams =0 and folder_id not in 
(
select f.folder_id from files f, folders fol, file_postprocessing fp where fol.project_id =201 and f.folder_id = fol.folder_id and 
f.file_id = fp.file_id and fp.post_step = 'id_manager_arches'
)





select f.folder_id from files f, folders fol where f.folder_id = fol.folder_id and (fol.project_id = 201 or fol.project_id = 186) and f.dams_uan is not null and SUBSTRING_INDEX(f.file_name, '_', 1) not in 
(
select id1_value from jpc_massdigi_ids jmi where jmi.id_relationship = 'refid_hmo' group by id1_value
)
group by folder_id 






select id1_value from jpc_massdigi_ids jmi where jmi.id_relationship = 'refid_hmo' and 
id1_value not in 
(
    select SUBSTRING_INDEX(f.file_name, '_', 1) as refid from files f, folders fol where f.folder_id = fol.folder_id and (fol.project_id = 201 or fol.project_id = 186) and f.dams_uan is not null
    

    )
    
    
    
select count(f.file_id) from files f, folders fol where f.folder_id = fol.folder_id and fol.folder_id in (select folder_id from folders where project_id = 201)
and f.dams_uan is not null














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
    case when fol.project_id = 201 then 'Priority One' when 
        fol.project_id = 186 then 'Pilot' END as stage, 
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
      AND (fol.project_id = 201 or fol.project_id = 186)
    AND f.dams_uan is not null 

 
 
 
select file_id from file_postprocessing fp where post_step = 'arches_record' and post_results = 0 and file_id in 
(select file_id from files where folder_id in (select folder_id from folders where project_id = 201))
and file_id in (select file_id from files where dams_uan is not null)
)
