with data1 as (select id1_value as refid, id2_value as hmo from jpc_massdigi_ids jmi where 
	id_relationship  = 'refid_hmo'),
	
	data2 as (select id1_value as hmo, id2_value as tif from jpc_massdigi_ids jmi where 
	id_relationship  = 'hmo_tif'),
	
	data3 as (select id1_value as tif, id2_value as dams from jpc_massdigi_ids jmi where 
	id_relationship  = 'tif_dams')
	
select data1.refid, data1.hmo, data2.tif, data3.dams
from data1, data2, data3 
where data1.hmo=data2.hmo and data2.tif=data3.tif