import pkg_resources as pr

def load_entry_point(group, name, human_name):
    list_ = list(pr.iter_entry_points(
        group=group, name=name
    ))
    if not list_:
        raise ValueError(
            'Sorry, {0} {1} is not installed'.format(human_name, name)
        )
    if len(list_) > 1:
        warnings.warn(
            'More than one {0} found matching {1}. Using the first one '
            'found.'.format(human_name, name)
        )
    return list_[0].load()
