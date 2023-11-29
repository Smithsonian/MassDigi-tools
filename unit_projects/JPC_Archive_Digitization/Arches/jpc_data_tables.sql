
CREATE FUNCTION updated_at_jpc() RETURNS TRIGGER
    LANGUAGE plpgsql
    AS $$
BEGIN
  NEW.updated_at := NOW();
  RETURN NEW;
END;
$$;


DROP TABLE IF EXISTS jpc_data_aspace;
CREATE TABLE jpc_data_aspace (
    table_id uuid NOT NULL DEFAULT uuid_generate_v4() PRIMARY KEY,
    refid text NOT NULL UNIQUE,
    archive_box text NOT NULL,
    archive_type text,
    archive_folder text NOT NULL,
    unit_title text,
    url text,
    notes text,
    updated_at timestamp with time zone DEFAULT NOW()
);
CREATE INDEX jpc_data_aspace_refid_idx ON jpc_data_aspace USING BTREE(refid);
CREATE INDEX jpc_data_aspace_box_idx ON jpc_data_aspace USING BTREE(archive_box);
CREATE INDEX jpc_data_aspace_type_idx ON jpc_data_aspace USING BTREE(archive_type);
CREATE INDEX jpc_data_aspace_folder_idx ON jpc_data_aspace USING BTREE(archive_folder);
CREATE INDEX jpc_data_aspace_name_idx ON jpc_data_aspace USING BTREE(unit_title);


create trigger trigger_jpc_aspace before
update on jpc_data_aspace for each row execute procedure updated_at_jpc();




DELETE FROM data_reports WHERE project_id = 144;

INSERT INTO data_reports
    (project_id, report_title, query, query_updated, query_api)
    VALUES
           (144,
            'ASpace RefIDs',
            'SELECT unit_title AS "Title", ''<pre><a href="'' || url || ''" target="_blank" title="Link to ASpace record for the folder">'' || refid || ''</a></pre>'' as refid, archive_type as "Type", archive_box AS "Box", archive_folder AS "Folder" FROM jpc_data_aspace',
            'SELECT TO_CHAR(MAX(updated_at), ''YYYY-Mon-DD HH24:MI'') as updated_at FROM jpc_data_aspace',
            'SELECT unit_title, url, refid, archive_type, archive_box, archive_folder FROM jpc_data_aspace'
            );

