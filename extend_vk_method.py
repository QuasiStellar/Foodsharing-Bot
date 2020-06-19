# TODO: may ship or duplicate elements, fix it
def _get_whole_list(*, fetching_func, max_count):
    offset = 0
    while True:
        result = fetching_func(offset=offset, count=max_count)
        if not result:
            break
        yield from result
        offset += max_count


def extend_vk_method(vk_method, *, max_count):
    return lambda **extended_vk_method_kwargs: _get_whole_list(
        fetching_func=lambda **fetching_func_kwargs:
            vk_method(**extended_vk_method_kwargs, **fetching_func_kwargs)["items"],
        max_count=max_count
    )
