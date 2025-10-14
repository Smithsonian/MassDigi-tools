# Move images

These scripts will take CSV with filenames to rename. This is for the CHSDM Card Catalog digitization project.

Scripts to run, in order:

 * `move_cards_smallset.py` - move files from a small list (~300)
 * `move_cards_excluded.py` - move files from a small list of excluded filenames
 * `move_cards_list.py` - move files from a list of ~3940
 * `move_cards_allrest.py` - move all the rest of the files

Results:

 * `smallset_duperow.txt` - 5 - Same name in multiple rows in the small list (~300)
 * `smallset_missing.txt` - 3 - Filenames in the small list not found
 * `excluded_duperow.txt` - 4 - Same name in multiple rows in the list of excluded filenames
 * `excluded_missing.txt` - 6 - Filenames in the small list not found
 * `duperow.txt` - 2 - Same name in multiple rows in the list of ~3940
 * `missing.txt` - 274 - Filenames in the list of ~3940 not found

File counts:

 * `consolidated` - 97,188
 * `odd_names` - 4,343 - Files with "Missing" or "NA" in the name
 * `compare_dupes` - Dupes from list of ~3940:
    * `real_duplicates` - 3,313 - Same hash or high similarity
    * `duplicates` - 314 - Filename duplicates with different contents
 * `compare_dupes_allrest` - Dupes from all other files:
    * `real_duplicates` - 9,918 - Same hash or high similarity
    * `duplicates_allrest` - 3,980 - Filename duplicates with different contents
