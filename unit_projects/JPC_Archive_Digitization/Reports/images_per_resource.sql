-- report by resource from ASpace
select 
	jar.resource_id,
	jar.resource_title,
	count(distinct f.file_id) as no_images,
	count(distinct SUBSTRING_INDEX(f.file_name, '_', 2)) as no_items,
	count(distinct SUBSTRING_INDEX(f.file_name, '_', 1)) as no_folders
from 
	files f,
	folders fol,
	jpc_aspace_resources jar,
	jpc_aspace_data jad 
where 
	(fol.project_id = 201 or fol.project_id = 186) and
	fol.folder_id = f.folder_id and 
	jar.resource_id = jad.resource_id and 
	jad.refid = SUBSTRING_INDEX(f.file_name, '_', 1)
group by 
	jar.resource_id,
	jar.resource_title



-- update
SELECT max(f.updated_at) as updated_at from files f, folders fol where f.folder_id = fol.folder_id and (fol.project_id = 186 or fol.project_id = 201)
