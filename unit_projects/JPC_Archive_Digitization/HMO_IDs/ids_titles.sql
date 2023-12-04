with data as (SELECT id1_value as refid, id2_value as hmo FROM dpo_osprey.jpc_massdigi_ids 
					where id_relationship = 'refid_hmo') 
             select d.*, 
             concat(j.unit_title, ' - Box ', j.archive_box, ' Folder ', j.archive_folder, ' Image ', 
             		LPAD(	
             		row_number() over (partition by refid order by d.refid, hmo),
             		4, '0')
             			) as unit_title, 
             j.archive_box, j.archive_folder 
             from data d, jpc_aspace_data j where d.refid=j.refid
             order by unit_title