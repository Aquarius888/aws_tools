#Settings for buildcopyaws
user = 'pavel.alexeev' #ADS user
password = "4rfD5tgH" #ADS password
url_ads = 'https://ads.lab.nordigy.ru/'
url_api_rn = 'api/v2/release-note/'
bld_link = '//builder.dins.ru/BIN/'
#lst_req = ['ACE'] #case sensitivy (without FAX, TAS - see lower)
lst_reg_tas_fax = ['TAS', 'FAX'] #if requires

#bucket = 'ads-builds-rc' # name of s3 bucket
#rn_name = 'monopod_9-2'

lst_req = ['ICA'] #case sensitivy (without FAX, TAS - see lower)

bucket = 'ads-builds-rc' # name of s3 bucket
rn_name = 'DN'

