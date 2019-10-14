def get_authors(author_string, model):
    if not author_string:
        return None
    name_type = ['last','first']
    author_list = []
    for author in author_string.split('and'):
        # author = author.split(',')
        # author = [author[0]] + author[1].split()
        # authors.append({key+'_name':name.strip().replace('.','') for key,name in zip(name_type,author)})

        author = author.split(',')
        author = [author[0]] + author[1].split()
        author = {key+'_name':name.strip().replace('.','') for key,name in zip(name_type,author)}


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
                    print(ValueError('Found more than one author by the name {} {}. Please double check'.format(author['last_name'],author['first_name'][0])))

    return author_list