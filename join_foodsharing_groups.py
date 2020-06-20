from extend_vk_method import extend_vk_method


def search_groups(query, *, vk):
    _extended_vk_search_groups = extend_vk_method(vk.groups.search, max_count=1000)
    return list(_extended_vk_search_groups(q=query))


def get_foodsharing_groups(*, vk):
    groups = search_groups(query="Фудшеринг", vk=vk) + search_groups(query="Отдам еду", vk=vk)
    groups = {frozenset(group.items()) for group in groups}
    groups = sorted(map(dict, groups), key=lambda group: group["id"])
    return groups
