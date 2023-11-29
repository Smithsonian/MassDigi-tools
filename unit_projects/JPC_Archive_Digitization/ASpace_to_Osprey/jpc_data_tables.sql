-- PostgreSQL version


CREATE FUNCTION updated_at_jpc() RETURNS TRIGGER
    LANGUAGE plpgsql
    AS $$
BEGIN
  NEW.updated_at := NOW();
  RETURN NEW;
END;
$$;





DROP TABLE IF EXISTS jpc_aspace_resources CASCADE;
CREATE TABLE jpc_aspace_resources (
    table_id uuid NOT NULL DEFAULT uuid_generate_v4() PRIMARY KEY,
    resource_id text NOT NULL UNIQUE,
    repository_id text NOT NULL,
    resource_title text NOT NULL,
    resource_tree text NOT NULL,
    updated_at timestamp with time zone DEFAULT NOW()
);
CREATE INDEX jpc_aspace_resources_tid_idx ON jpc_aspace_resources USING BTREE(table_id);
CREATE INDEX jpc_aspace_resources_resid_idx ON jpc_aspace_resources USING BTREE(resource_id);
CREATE INDEX jpc_aspace_resources_ead_idx ON jpc_aspace_resources USING BTREE(resource_eadid);

create trigger trigger_jpc_aspace_res before
update on jpc_aspace_resources for each row execute procedure updated_at_jpc();





DROP TABLE IF EXISTS jpc_aspace_data;
CREATE TABLE jpc_aspace_data (
    table_id uuid NOT NULL DEFAULT uuid_generate_v4() PRIMARY KEY,
    resource_id text NOT NULL REFERENCES jpc_aspace_resources(resource_id) ON DELETE CASCADE ON UPDATE CASCADE,
    refid text NOT NULL UNIQUE,
    archive_box text NOT NULL,
    archive_type text,
    archive_folder text NOT NULL,
    unit_title text,
    url text,
    notes text,
    updated_at timestamp with time zone DEFAULT NOW()
);
CREATE INDEX jpc_aspace_data_refid_idx ON jpc_aspace_data USING BTREE(refid);
CREATE INDEX jpc_aspace_data_resid_idx ON jpc_aspace_data USING BTREE(resource_id);
CREATE INDEX jpc_aspace_data_box_idx ON jpc_aspace_data USING BTREE(archive_box);
CREATE INDEX jpc_aspace_data_type_idx ON jpc_aspace_data USING BTREE(archive_type);
CREATE INDEX jpc_aspace_data_folder_idx ON jpc_aspace_data USING BTREE(archive_folder);
CREATE INDEX jpc_aspace_data_name_idx ON jpc_aspace_data USING BTREE(unit_title);


create trigger trigger_jpc_aspace before
update on jpc_aspace_data for each row execute procedure updated_at_jpc();











DELETE FROM data_reports WHERE project_id = 144;

INSERT INTO data_reports
    (project_id, report_title, report_title_brief, query, query_updated, query_api)
    (
        SELECT
            144,
            r.resource_title,
            'ASpace ' || r.resource_id,
            'SELECT unit_title AS "Title", ''<pre><a href="'' || url || ''" target="_blank" title="Link to ASpace record for the folder">'' || refid || ''</a></pre>'' as refid, archive_type as "Type", archive_box AS "Box", archive_folder AS "Folder" FROM jpc_aspace_data WHERE resource_id = ''' || r.resource_id || '''',
            'SELECT TO_CHAR(MAX(updated_at), ''YYYY-Mon-DD HH24:MI'') as updated_at FROM jpc_aspace_data WHERE resource_id = ''' || r.resource_id || '''',
            'SELECT unit_title, url, refid, archive_type, archive_box, archive_folder FROM jpc_aspace_data WHERE resource_id = ''' || r.resource_id || ''''
        FROM jpc_aspace_resources r
    );

