from itertools import takewhile

from vk_api import ApiError

from extend_vk_method import extend_vk_method


def _get_sorted_posts(posts):
    return sorted(
        posts,
        key=lambda post: (post["date"], post["owner_id"], post["id"]),
        reverse=True
    )


def _remove_duplicates_posts_and_sort(posts):
    posts = _get_sorted_posts(posts)
    if not posts:
        return []
    result = [posts[0]]
    get_post_id = lambda post: (post["owner_id"], post["id"])
    for prev_post, curr_post in zip(posts, posts[1:]):
        if get_post_id(curr_post) != get_post_id(prev_post):
            result.append(curr_post)
        else:
            result[-1] = curr_post
    return result


# TODO: if any post above became deleted during collection
#       this method will skip another post
def fetch_group_posts(group_id, *, time_begin, time_end, vk):
    if group_id <= 0:
        raise ValueError("group_id must be positive")
    get_wall = extend_vk_method(vk.wall.get, max_count=100)
    result_posts = takewhile(lambda post: post["date"] >= time_begin, get_wall(owner_id=-group_id))
    result_posts = filter(
        lambda post: time_begin <= post["date"] < time_end,
        result_posts
    )
    result_posts = _remove_duplicates_posts_and_sort(result_posts)
    return result_posts


def fetch_groups_posts(groups_ids, *, time_begin, time_end, vk):
    result_posts = []
    for group_id in groups_ids:
        try:
            group_posts = fetch_group_posts(group_id, time_begin=time_begin, time_end=time_end, vk=vk)
        except ApiError as e:
            print("fetch_groups_posts:", repr(e))
        else:
            result_posts.extend(group_posts)
    result_posts = _remove_duplicates_posts_and_sort(result_posts)
    return result_posts
