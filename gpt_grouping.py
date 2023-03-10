import numpy as np
import pyperclip
import ast


CATEGORIES = {'sports','food','geography','market','philosophy','animals',
              'sexual','violent','books_comics','q_and_a','hobbies','media',
              'tech','health_fitness','science','music','video_games',
              'stories','education','travel','religion','personal','vehicles',
              'comedy','medical','news','politics','fashion','professional',
              'other'}


def get_uncategorized(groups: dict):
    """Get the subreddits that were only grouped into 'other'"""
    uncat = groups['other']

    for g, srs in groups.items():
        if g == 'other':
            continue
        uncat = uncat.difference(srs)

    return uncat


def iterate_queries_till_full(original: set, groups: dict, categories=None):
    """
    Recursively generate ChatGPT queries, save them to clipboard, and prompt to
      add responses into @groups. Continues until all elements in @original are
      present in @groups.

    :param original: the full set of subreddits to group
    :param groups: already grouped subreddits, separated into categories
    :param categories: (optional) categories to use in query to ChatGPT
    :return: dictionary with all subreddits grouped
    """
    # TODO 3/9: very hacky I think; should switch to GPT api

    cats = CATEGORIES if categories is None else categories

    extracted = get_grouped_subreddits(groups) # all chatgpt grouped subreddits
    missing, added = get_missing_and_added(original, extracted)

    if len(missing) == 0:
        # all subreddits grouped, return grouping
        return groups

    chunks = batch_list(missing, batch_size=120)
    for c in chunks:
        e = query_prompt_and_extract(cats, c)
        if e is None:
            return groups

        update_group(groups, e)

    return iterate_queries_till_full(original, groups, categories)


def query_prompt_and_extract(categories, chunk):
    """
    Create a chatgpt grouping query and prompt to con
    """
    clipboard_query(categories, chunk)

    while True:
        response = input(
            'Enter "a" to save to clipboard again, "q" to quit, '
            'or paste string of dict response from ChatGPT: '
        )
        if response == 'a':
            clipboard_query(categories, chunk)
        elif response == 'q':
            return None
        else:
            try:
                d = string_to_dict(response)
                return d
            except Exception as e:
                print(f'Invalid string!\n{e.args}')
                continue


def clipboard_query(categories, chunk):
    """
    Copies the query straight to clipboard, just paste into ChatGPT. It's hacky
      and querying the API would have been the cleaner solution, but this is a
      one-off task and also required a lot of live communication with the model
      to ensure the output was how I wanted it.
    """
    pyperclip.copy(format_query(categories, chunk))


def format_query(categories, chunk):
    """
    The formatting of the query ensures a few things: that the more precise model
      is used for the grouping, that every subreddit is categorized at least once,
      and subreddits are categorized into all relevant categories. And obviously
      the output is a dict with set values and categories as keys.
    """
    return(f'I will provide you a list of subreddits, group them into '
           f'these categories: {categories}. Format the output as '
           f'follows: put the categorizations into a python dict with '
           f'category as key and the subreddits as values in a set. Assign the subreddits into all '
           f'relevant categories. Make sure all subreddits are placed '
           f'into at least 1 category. Dont do any special visual formatting '
           f'like putting set elements on new lines. Here are the '
           f'subreddits: {chunk}')


def get_missing_and_added(original: set, processed: set):
    miss = original.difference(processed)
    added = processed.difference(original)

    return miss, added


def batch_list(data, batches=None, batch_size=None):
    """Batch @data into a specific amount of @batches or by @batch_size"""
    if batches is None and batch_size is None:
        return data

    d = data
    if isinstance(data, set):
        d = list(d)

    bs = []
    if batches is not None:
        bs = np.array_split(d, batches)

    elif batch_size is not None:
        batches = int(np.ceil(len(data)/batch_size))

        for i in range(batches):
            start = i*batch_size
            end = (i+1)*batch_size

            bs.append(d[start:end])

    return bs


def get_grouped_subreddits(groups: dict):
    """Return a set of all subreddits that are in @groups"""
    srs = set()
    for g in groups.values():
        srs.update(g)

    return srs


def string_to_dict(s):
    """Convert a string representing a dictionary back into dict"""
    d = ast.literal_eval(s)
    return d


def update_group(gs, new_data):
    for g,l in new_data.items():
        try:
            gs[g].update(l)
        except KeyError:
            gs[g] = l


# if __name__ == "__main__":
#     s = "{ 'music': {'Jazz', 'EDM'}, 'hobbies': {'modelmakers', 'Scotch', 'investing', 'skyrimmods', 'bourbon', 'buffy', 'starcraft', 'astrophotography', 'gamedesign', 'AnimalCrossing', 'Gundam', 'drumcorps'}, 'health_fitness': {'loseit', 'Supplements'}, 'science': {'AskScienceDiscussion', 'statistics'}, 'politics': {'Shitstatistssay'}, 'education': {'uwaterloo', 'AskCulinary'}, 'vehicles': {'engineering', 'SelfDrivingCars', 'Honda', 'BMW', 'MosinNagant', 'AirForce'}, 'media': {'Toonami', 'GameDeals', 'NetflixBestOf'}, 'violent': {'NSFW_GIF'}, 'other': {'firefox', 'caps', 'cableporn', 'CableManagement', 'Infographics', 'Surface', 'AndroidQuestions', 'Hotchickswithtattoos'}, 'news': {'UpliftingNews'}, 'comedy': {'AntiJokes', 'shittyadviceanimals', 'futurama', 'Badphilosophy', 'DoctorWhumour'}, 'sports': {'MLS', 'leagueoflegends', 'bengals', 'chelseafc', 'Colts'}, 'fashion': {'frugalmalefashion'}, 'sexual': {'LadyBoners', 'ABDL', 'PurplePillDebate', 'gonewildaudio'}, 'books_comics': {'talesfromcallcenters'}, 'geography': {'jacksonville', 'batonrouge', 'Atlanta', 'belgium', 'Norway', 'sandiego', 'Scotland'}, 'food': {'AskCulinary', 'EmmaWatson', 'beerporn'}, 'animals': {'penguins'}, 'stories': {'Thetruthishere', 'forwardsfromgrandma', 'Dreams'}, 'video_games': {'Starcitizen_trades', 'ChivalryGame', 'lostgeneration', 'dawngate', 'spaceporn', 'dayz', 'orlando', 'metalgearsolid', 'Nexus5'}, 'philosophy': {'INTP', 'Badphilosophy', 'DebateAChristian'}, 'personal': {'socialanxiety', 'resumes', 'tall', 'peacecorps', 'selfimprovement'}, 'market': {'investing', 'Shave_Bazaar', 'BitcoinMining'}, 'religion': {'DebateAChristian'}, 'medical': {'birthcontrol', 'medicine'}, 'q_and_a': {'AskCulinary', 'AskScienceDiscussion', 'tipofmytongue'}, 'tech': {'firefox', 'tasker', 'AndroidQuestions', 'Surface'}, 'professional': {'resumes', 'belgium'}, 'travel': {'AppalachianTrail'} }"
#     s1 = string_to_dict(s)
#     print(type(s1), s1.keys())
