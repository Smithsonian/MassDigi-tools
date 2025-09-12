select 
	u.username, p.project_title, count(*) as no_files, count(distinct qcfol.folder_id) as no_folders
from qc_files qcf, qc_folders qcfol, users u, projects p, folders fold
 where qcf.folder_id = qcfol.folder_id  
     and (p.project_id = 186 or p.project_id = 201 or p.project_id = 220)
     and p.project_id = fold.project_id 
     and fold.folder_id = qcf.folder_id
     and qcf.qc_by = u.user_id
     group by p.project_id, u.username, p.project_title
     order by p.project_id, u.username;

--
select u.username, p.project_title, count(*) as no_files, count(distinct qcfol.folder_id) as no_folders from qc_files qcf, qc_folders qcfol, users u, projects p, folders fold where qcf.folder_id = qcfol.folder_id and (p.project_id = 186 or p.project_id = 201 or p.project_id = 220) and p.project_id = fold.project_id and fold.folder_id = qcf.folder_id and qcf.qc_by = u.user_id group by p.project_id, u.username, p.project_title order by p.project_id, u.username;



-- update
select max(qcf.updated_at)
from qc_files qcf, qc_folders qcfol, projects p, folders fold
 where qcf.folder_id = qcfol.folder_id  
     and (p.project_id = 186 or p.project_id = 201 or p.project_id = 220)
     and p.project_id = fold.project_id 
     and fold.folder_id = qcf.folder_id;

--
select max(qcf.updated_at) as updated_at from qc_files qcf, qc_folders qcfol, projects p, folders fold where qcf.folder_id = qcfol.folder_id and (p.project_id = 186 or p.project_id = 201 or p.project_id = 220) and p.project_id = fold.project_id and fold.folder_id = qcf.folder_id;
