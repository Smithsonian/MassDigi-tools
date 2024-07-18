with data1 as (select id1_value as refid, id2_value as hmo from jpc_massdigi_ids jmi where 
	id_relationship  = 'refid_hmo'),
	
	data2 as (select id1_value as hmo, id2_value as tif from jpc_massdigi_ids jmi where 
	id_relationship  = 'hmo_tif'),
	
	data3 as (select id1_value as tif, id2_value as dams from jpc_massdigi_ids jmi where 
	id_relationship  = 'tif_dams')
	
select data1.refid, data1.hmo, data2.tif, data3.dams
from data1, data2, data3 
where data1.hmo=data2.hmo and data2.tif=data3.tif
and data1.refid not in ('abdf9b232cdeb401ced7e386d97c013b', 'a48abb18653b3f2d7ec1473e63755e6b', 'a9e4073af3ac29d2d8601a8c06be5646', 'da0c77f6628da9148489b5ee41786cde', '4945c6702e1495b214b24b4bbc71f460');
