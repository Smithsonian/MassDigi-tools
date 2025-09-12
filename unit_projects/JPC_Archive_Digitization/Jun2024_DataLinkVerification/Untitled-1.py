
import pandas


folders = pandas.read_csv("../Jun2024_DataLinkVerification/jpc_prod_folders.csv")


def count_idmanager(folder_id):
    r = requests.get("https://staging-services.jpcarchive.org/id-management/groups/dpo-jpca-fol{}".format(folder_id))
    results = json.loads(r.text)
    results1 = results['total']
    r = requests.get("https://staging-services.jpcarchive.org/id-management/groups/dpo-jpca-fol{}".format(folder_id))
    results = json.loads(r.text)
    results1 = results['total']
    Group: dpo-jpca-20240516

    return results['total']


folders['expected'] = folders.apply(lambda row: row['no_files'] * 2, axis=1)

folders['id_manager'] = folders.apply(lambda row: count_idmanager(row['folder_id']), axis=1)
