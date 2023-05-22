#!/usr/bin/env python

import argparse
import base64
import copy
import pandas as pd
import pycountry
import yaml

from geopy.geocoders import Nominatim
from github import Github
from pathlib import Path

ACTUAL_COHORT = 7

ROLES = ['role', 'participant', 'mentor', 'expert', 'speaker', 'facilitator', 'organizer']

# copied from https://github.com/jefftune/pycountry-convert/blob/master/pycountry_convert/country_alpha2_to_continent.py
COUNTRY_ALPHA2_TO_CONTINENT = {
    'AB': 'Asia',
    'AD': 'Europe',
    'AE': 'Asia',
    'AF': 'Asia',
    'AG': 'North America',
    'AI': 'North America',
    'AL': 'Europe',
    'AM': 'Asia',
    'AO': 'Africa',
    'AR': 'South America',
    'AS': 'Oceania',
    'AT': 'Europe',
    'AU': 'Oceania',
    'AW': 'North America',
    'AX': 'Europe',
    'AZ': 'Asia',
    'BA': 'Europe',
    'BB': 'North America',
    'BD': 'Asia',
    'BE': 'Europe',
    'BF': 'Africa',
    'BG': 'Europe',
    'BH': 'Asia',
    'BI': 'Africa',
    'BJ': 'Africa',
    'BL': 'North America',
    'BM': 'North America',
    'BN': 'Asia',
    'BO': 'South America',
    'BQ': 'North America',
    'BR': 'South America',
    'BS': 'North America',
    'BT': 'Asia',
    'BV': 'Antarctica',
    'BW': 'Africa',
    'BY': 'Europe',
    'BZ': 'North America',
    'CA': 'North America',
    'CC': 'Asia',
    'CD': 'Africa',
    'CF': 'Africa',
    'CG': 'Africa',
    'CH': 'Europe',
    'CI': 'Africa',
    'CK': 'Oceania',
    'CL': 'South America',
    'CM': 'Africa',
    'CN': 'Asia',
    'CO': 'South America',
    'CR': 'North America',
    'CU': 'North America',
    'CV': 'Africa',
    'CW': 'North America',
    'CX': 'Asia',
    'CY': 'Asia',
    'CZ': 'Europe',
    'DE': 'Europe',
    'DJ': 'Africa',
    'DK': 'Europe',
    'DM': 'North America',
    'DO': 'North America',
    'DZ': 'Africa',
    'EC': 'South America',
    'EE': 'Europe',
    'EG': 'Africa',
    'ER': 'Africa',
    'ES': 'Europe',
    'ET': 'Africa',
    'FI': 'Europe',
    'FJ': 'Oceania',
    'FK': 'South America',
    'FM': 'Oceania',
    'FO': 'Europe',
    'FR': 'Europe',
    'GA': 'Africa',
    'GB': 'Europe',
    'GD': 'North America',
    'GE': 'Asia',
    'GF': 'South America',
    'GG': 'Europe',
    'GH': 'Africa',
    'GI': 'Europe',
    'GL': 'North America',
    'GM': 'Africa',
    'GN': 'Africa',
    'GP': 'North America',
    'GQ': 'Africa',
    'GR': 'Europe',
    'GS': 'South America',
    'GT': 'North America',
    'GU': 'Oceania',
    'GW': 'Africa',
    'GY': 'South America',
    'HK': 'Asia',
    'HM': 'Antarctica',
    'HN': 'North America',
    'HR': 'Europe',
    'HT': 'North America',
    'HU': 'Europe',
    'ID': 'Asia',
    'IE': 'Europe',
    'IL': 'Asia',
    'IM': 'Europe',
    'IN': 'Asia',
    'IO': 'Asia',
    'IQ': 'Asia',
    'IR': 'Asia',
    'IS': 'Europe',
    'IT': 'Europe',
    'JE': 'Europe',
    'JM': 'North America',
    'JO': 'Asia',
    'JP': 'Asia',
    'KE': 'Africa',
    'KG': 'Asia',
    'KH': 'Asia',
    'KI': 'Oceania',
    'KM': 'Africa',
    'KN': 'North America',
    'KP': 'Asia',
    'KR': 'Asia',
    'KW': 'Asia',
    'KY': 'North America',
    'KZ': 'Asia',
    'LA': 'Asia',
    'LB': 'Asia',
    'LC': 'North America',
    'LI': 'Europe',
    'LK': 'Asia',
    'LR': 'Africa',
    'LS': 'Africa',
    'LT': 'Europe',
    'LU': 'Europe',
    'LV': 'Europe',
    'LY': 'Africa',
    'MA': 'Africa',
    'MC': 'Europe',
    'MD': 'Europe',
    'ME': 'Europe',
    'MF': 'North America',
    'MG': 'Africa',
    'MH': 'Oceania',
    'MK': 'Europe',
    'ML': 'Africa',
    'MM': 'Asia',
    'MN': 'Asia',
    'MO': 'Asia',
    'MP': 'Oceania',
    'MQ': 'North America',
    'MR': 'Africa',
    'MS': 'North America',
    'MT': 'Europe',
    'MU': 'Africa',
    'MV': 'Asia',
    'MW': 'Africa',
    'MX': 'North America',
    'MY': 'Asia',
    'MZ': 'Africa',
    'NA': 'Africa',
    'NC': 'Oceania',
    'NE': 'Africa',
    'NF': 'Oceania',
    'NG': 'Africa',
    'NI': 'North America',
    'NL': 'Europe',
    'NO': 'Europe',
    'NP': 'Asia',
    'NR': 'Oceania',
    'NU': 'Oceania',
    'NZ': 'Oceania',
    'OM': 'Asia',
    'OS': 'Asia',
    'PA': 'North America',
    'PE': 'South America',
    'PF': 'Oceania',
    'PG': 'Oceania',
    'PH': 'Asia',
    'PK': 'Asia',
    'PL': 'Europe',
    'PM': 'North America',
    'PR': 'North America',
    'PS': 'Asia',
    'PT': 'Europe',
    'PW': 'Oceania',
    'PY': 'South America',
    'QA': 'Asia',
    'RE': 'Africa',
    'RO': 'Europe',
    'RS': 'Europe',
    'RU': 'Europe',
    'RW': 'Africa',
    'SA': 'Asia',
    'SB': 'Oceania',
    'SC': 'Africa',
    'SD': 'Africa',
    'SE': 'Europe',
    'SG': 'Asia',
    'SH': 'Africa',
    'SI': 'Europe',
    'SJ': 'Europe',
    'SK': 'Europe',
    'SL': 'Africa',
    'SM': 'Europe',
    'SN': 'Africa',
    'SO': 'Africa',
    'SR': 'South America',
    'SS': 'Africa',
    'ST': 'Africa',
    'SV': 'North America',
    'SY': 'Asia',
    'SZ': 'Africa',
    'TC': 'North America',
    'TD': 'Africa',
    'TG': 'Africa',
    'TH': 'Asia',
    'TJ': 'Asia',
    'TK': 'Oceania',
    'TM': 'Asia',
    'TN': 'Africa',
    'TO': 'Oceania',
    'TP': 'Asia',
    'TR': 'Asia',
    'TT': 'North America',
    'TV': 'Oceania',
    'TW': 'Asia',
    'TZ': 'Africa',
    'UA': 'Europe',
    'UG': 'Africa',
    'US': 'North America',
    'UY': 'South America',
    'UZ': 'Asia',
    'VC': 'North America',
    'VE': 'South America',
    'VG': 'North America',
    'VI': 'North America',
    'VN': 'Asia',
    'VU': 'Oceania',
    'WF': 'Oceania',
    'WS': 'Oceania',
    'XK': 'Europe',
    'YE': 'Asia',
    'YT': 'Africa',
    'ZA': 'Africa',
    'ZM': 'Africa',
    'ZW': 'Africa',
}

def read_yaml_file(fp, ref):
    '''
    Read a YAML file at a given git commit

    :param fp: path to file on GitHub
    :param ref: name of the commit/branch/tag

    :return: set with contributor ids
    '''
    file_content = repo.get_contents(fp, ref=ref).content
    decoded_file_content = base64.b64decode(file_content)
    return yaml.load(decoded_file_content, Loader=yaml.FullLoader)


def update_people_info(p_list, p_dict, cohort_id, role, value):
    '''
    Update people attribute for a cohort

    :param p_list: list of people id to update
    :param p_dict: dictionary with people information
    :param role: status to add
    :param cohort_id: concerned cohort
    '''
    for p in p_list:
        if p is None:
            continue
        if p not in p_dict:
            print(f"{p} not found in people")
            continue
        p_dict[p][f'ols-{cohort_id}-role'].append(role)
        if role == 'participant' or role == 'mentor':
            p_dict[p][f'ols-{cohort_id}-{role}'].append(value)
        else:
            p_dict[p][f'ols-{cohort_id}-{role}'] = value


def get_people_names(p_list, p_dict):
    '''
    Get names of peoke

    :param p_list: list of people id
    :param p_dict: dictionary with people information
    '''
    names = []
    for p in p_list:
        if p is None:
            names.append(None)
        elif p not in p_dict:
            print(f"{p} not found in people")
            names.append(None)
        else:
            names.append(f"{p_dict[p]['first-name']} {p_dict[p]['last-name']}")
    return names


def get_people():
    '''
    Get and format people information
    '''
    print("Get and format people information")
    # get people information
    people = read_yaml_file("_data/people.yaml", "main")
    # initialize Nominatim API
    geolocator = Nominatim(user_agent="MyApp")
    # format information
    for key, value in people.items():
        # remove some keys
        value.pop('affiliation', None)
        value.pop('bio', None)
        value.pop('orcid', None)
        value.pop('twitter', None)
        value.pop('website', None)
        value.pop('github', None)
        value.pop('title', None)
        value.pop('expertise', None)
        # get country alpha_3 and continent
        if 'country' in value:
            country = pycountry.countries.get(name=value['country'])
            if country is None:
                country = pycountry.countries.get(common_name=value['country'])
                if country is None:
                    print(f"{value['country']} not found")
            else:
                value['country-alpha_3'] = country.alpha_3
                if country.alpha_2 not in COUNTRY_ALPHA2_TO_CONTINENT:
                    print(f"No continent found for {value['country']} / {country.alpha_2}")
                else:
                    value['continent'] = COUNTRY_ALPHA2_TO_CONTINENT[country.alpha_2]
        # get city
        if 'city' in value:
            location = geolocator.geocode(value['city'])
            if location is None:
                print(f"{value['city']} not found")
            else:
                value['longitude'] = location.longitude
                value['latitude'] = location.latitude
        # add space for cohorts
        for i in range(1, ACTUAL_COHORT+1):
            value[f'ols-{i}-role'] = []
            value[f'ols-{i}-participant'] = []
            value[f'ols-{i}-mentor'] = []
            value[f'ols-{i}-expert'] = None
            value[f'ols-{i}-speaker'] = None
            value[f'ols-{i}-facilitator'] =  None
            value[f'ols-{i}-organizer'] =  None

    return people


def extract_cohort_information(people):
    '''
    Get cohort and project informations
    '''
    print("Get cohort and project informations")
    projects = []
    for i in range(1, ACTUAL_COHORT+1):
        print(f"OLS {i}")
        # extract experts, facilitators, organizers from metadata
        metadata = read_yaml_file(f"_data/ols-{i}-metadata.yaml" , "main")
        update_people_info(metadata['experts'], people, i, 'expert', 'expert')
        if 'facilitators' in metadata:
            update_people_info(metadata['facilitators'], people, i, 'facilitator', 'facilitator')
        update_people_info(metadata['organizers'], people, i, 'organizer',  'organizer')
        # extract participants, mentors from projects
        # extract project details
        cohort_projects = read_yaml_file(f"_data/ols-{i}-projects.yaml", "main")
        for p in cohort_projects:
            # update participant and mentor information
            update_people_info(p['participants'], people, i, 'participant', p['name'])
            update_people_info(p['mentors'], people, i, 'mentor', p['name'])
            # get project details
            pr = copy.copy(p)
            pr['participants'] = get_people_names(p['participants'], people)
            pr['mentors'] = get_people_names(p['mentors'], people)
            pr['cohort'] = i
            pr['keywords'] = p['keywords'] if 'keywords' in p else []
            projects.append(pr)
        # extract speakers from schedule
        schedule = read_yaml_file(f"_data/ols-{i}-schedule.yaml", "main")
        for w, week in schedule['weeks'].items():
            for c in week['calls']:
                if c['type'] == 'Cohort' and 'resources' in c and c['resources'] is not None:
                    for r in c['resources']:
                        if r['type'] == 'slides' and 'speaker' in r and r['speaker'] is not None:
                            update_people_info([r['speaker']], people, i,'speaker', 'speaker')
    return projects, people


def format_people_per_cohort(people, projects):
    '''
    Format to get people with their location and cohort and role
    (1 entry per person, per cohort, per role)
    '''
    people_per_cohort = []
    for key, value in people.items():
        info = {'id': key}
        # get localisation information
        for e in ['country', 'country-alpha_3', 'city', 'longitude', 'latitude']:
            info[e] = value[e] if e in value else None
        # get cohort participation
        for i in range(1, ACTUAL_COHORT+1):
            cohort = f'ols-{i}'
            el = f'ols-{i}-role'
            if el in value and len( value[el]) > 0:
                for r in value[el]:
                    t_info = copy.copy(info)
                    t_info['cohort'] = i
                    t_info['role'] = r
                    people_per_cohort.append(t_info)
    return people_per_cohort


def export_people_per_roles(people_df, out_dp):
    '''
    Export people per role
    '''
    print("Export people per role")
    people_info_df = people_df[[
        'city',
        'country',
        'first-name',
        'last-name',
        'pronouns',
        'country-alpha_3',
        'continent',
        'longitude',
        'latitude']]
    out_dp = out_dp / Path("roles")
    out_dp.mkdir(parents=True, exist_ok=True)
    for r in ROLES:
        role_df = people_df.filter(regex = r)
        role_df = role_df[role_df.filter(regex = r).notna().any(axis=1)]
        for i in range(1,ACTUAL_COHORT+1):
            role_df.rename(columns={f"ols-{i}-{r}": f"ols-{i}"}, inplace=True)
        df = pd.merge(
            people_info_df,
            role_df,
            left_index=True,
            right_index=True,
            how="inner")

        print(df.shape)
        fp = Path(out_dp) / Path(f"{r}.csv")
        df.to_csv(fp)


def get_library(out_fp):
    '''
    Get library to a CSV
    '''
    library = read_yaml_file('_data/library.yaml', 'catalog')
    # flatten the library
    flat_library = []
    for tag, t_v in library.items():
        for subtag, st_v in t_v.items():
            for v in st_v:
                v['tag'] = tag
                v['subtag'] = subtag
                flat_library.append(v)
    # transform to data frame to export it to csv
    library_df = pd.DataFrame(flat_library)
    library_df.to_csv(out_fp)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract data from website into CSV files')
    parser.add_argument('-t', '--token', help="GitHub token", required=True)
    parser.add_argument('-o', '--out', help="Path to output folder", required=True)
    args = parser.parse_args()

    # connect to GitHub
    g = Github(args.token)
    # to get limit of API request: g.get_rate_limit()
    # retrieve the hub repository
    repo = g.get_user("open-life-science").get_repo("open-life-science.github.io")

    # get people information
    people = get_people()

    # get cohort and project informations
    projects, people = extract_cohort_information(people)

    # format people / project information per cohort
    people_per_cohort = format_people_per_cohort(people, projects)

    # export people information to CSV file
    people_df = pd.DataFrame.from_dict(people, orient='index')
    for i in range(1, ACTUAL_COHORT+1):
        people_df[f'ols-{i}-role'] = people_df[f'ols-{i}-role'].apply(lambda x: ', '.join([str(i) for i in x]) if len(x)>0 else None)
        people_df[f'ols-{i}-participant'] = people_df[f'ols-{i}-participant'].apply(lambda x: ', '.join([str(i) for i in x]) if len(x)>0 else None)
        people_df[f'ols-{i}-mentor'] = people_df[f'ols-{i}-mentor'].apply(lambda x: ', '.join([str(i) for i in x]) if len(x)>0 else None)
    people_fp = Path(args.out) / Path('people.csv')
    people_df.to_csv(people_fp)

    # export project information to CSV file
    project_df = pd.DataFrame(projects)
    project_df['participants'] = project_df['participants'].apply(lambda x: ', '.join([str(i) for i in x]))
    project_df['mentors'] = project_df['mentors'].apply(lambda x: ', '.join([str(i) for i in x]))
    project_df['keywords'] = project_df['keywords'].apply(lambda x: ', '.join([str(i) for i in x]))
    project_fp = Path(args.out) / Path('projects.csv')
    project_df.to_csv(project_fp)

    # export people per cohort
    people_per_cohort_df = pd.DataFrame(people_per_cohort)
    people_per_cohort_fp = Path(args.out) / Path('people_per_cohort.csv')
    people_per_cohort_df.to_csv(people_per_cohort_fp)

    # export people per role
    export_people_per_roles(people_df, args.out)

    # get and export video library
    get_library(Path(args.out) / Path('library.csv'))
