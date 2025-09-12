-- dpo_osprey.jpc_aspace_boxes definition

CREATE TABLE `jpc_aspace_boxes` (
  `project_folder` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `box` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `archive_box` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


insert into jpc_aspace_boxes (project_folder, box, archive_box) (
with data as (select project_folder, 
	replace(
	replace(
	replace(
	replace(
	replace(
		replace(
		SUBSTRING_INDEX(SUBSTRING_INDEX(project_folder, '_', -4), '_202', 1) 
		, '_', '-')
	, '-a', '')
	, '-b', '')
	, '-c', '')
	, '-d', '')
	, '-e', '')
		box from folders where project_id = 220)


select d.*, jad.archive_box from data d left join jpc_aspace_data jad on lower(d.box)=lower(jad.archive_box) 
group by d.project_folder, d.box, jad.archive_box);