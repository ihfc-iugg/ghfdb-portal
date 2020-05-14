import bibtexparser as bib
import bibtexparser.customization as custom
import re

def getnames(names):
    """Convert people names as surname, firstnames
    or surname, initials.

    :param names: a list of names
    :type names: list
    :returns: list -- Correctly formated names

    .. Note::
        This function is known to be too simple to handle properly
        the complex rules. We would like to enhance this in forthcoming
        releases.
    """
    tidynames = []
    for namestring in names:
        namestring = namestring.strip()
        if len(namestring) < 1:
            continue
        if ',' in namestring:
            namesplit = namestring.split(',', 1)
            last = namesplit[0].strip()
            firsts = [i.strip() for i in namesplit[1].split()]
        else:
            namesplit = namestring.split()
            last = namesplit.pop()
            firsts = [i.replace('.', '. ').strip() for i in namesplit]
        if last in ['jnr', 'jr', 'junior']:
            last = firsts.pop()

        prefixes = ['von', 'ben', 'van', 'der', 'de', 'la', 'le']
        
        for item in firsts:
            if item.lower() in prefixes:
                last = firsts.pop().lower() + ' ' + last
        if len(last.split(' ')) > 1:
            tmp = []
            for item in last.split(' '):
                if item.lower() in prefixes:
                    tmp.append(item.lower())
                else:
                    tmp.append(item)
            last = ' '.join(tmp)

        tidynames.append(last + ", " + ' '.join(firsts))
    return tidynames

def get_author_list(entry_dict):
    """
    Split author field into a list of "Name, Surname".

    :param entry_dict: the record.
    :returns: list of dicts containing author information. returns empty list if no author information is present

    """
    if "author" in entry_dict:

        if entry_dict["author"]:
            # remove these characters from the author entry for consistency
            for char in ['{','}','.']:
                entry_dict['author'] = entry_dict['author'].replace(char,'')

            # entry_dict['author'] = entry_dict['author'].replace('Von','von')


            author_list = getnames([i.strip() for i in entry_dict["author"].replace('\n', ' ').split(" and ")])
            authors = []
            for name in author_list:
                # split the current author into first, middle and last names
                name = custom.splitname(name, strict_mode=False)
                # append to author list
                # if name['von']
                first = name['first']
                if first:
                    first = first[0]
                
                middle = ''
                if len(name['first']) > 1:
                    middle = ' '.join(name['first'][1:])

                last = name['last'][0]
                if name['von']:
                    last = name['von'][0] + ' ' +  last

                authors.append({
                    'first_name': first,
                    'middle_name': middle,
                    'last_name': last
                })

            return authors
        else:
            del entry_dict["author"]
            return []

def get_author_objects(entry_dict, model):

    authors = get_author_list(entry_dict)
    if not authors:
        return
    author_list = []
    for author in authors:

        try:
            author_list.append(model.objects.update_or_create(last_name=author['last_name'],defaults=author)[0])
        except model.MultipleObjectsReturned:
            try: 
                author_list.append(model.objects.update_or_create( last_name=author['last_name'],
                                                                    first_name__startswith=author['first_name'][0],
                                                                    defaults=author)[0])
            except model.MultipleObjectsReturned:
                try:
                    author_list.append(model.objects.update_or_create( last_name=author['last_name'],
                                                                        first_name=author['first_name'],
                                                                        defaults=author)[0])
                except model.MultipleObjectsReturned:

                    try:
                        author_list.append(model.objects.update_or_create( last_name=author['last_name'],
                                                                            first_name=author['first_name'],
                                                                            middle_name__startswith=author['middle_name'][0],
                                                                            defaults=author)[0])

                    except model.MultipleObjectsReturned:
                        raise ValueError('Found more than one author by the name {} {}. Please double check'.format(author['last_name'],author['first_name'][0]))

    return author_list
