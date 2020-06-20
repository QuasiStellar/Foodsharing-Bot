def fetch_new_posts(time_begin, time_end, *, vk):
    result_posts = vk.newsfeed.get(filters=["post"], count=100)["items"]  # TODO: don't skip posts
    for post in result_posts:
        post["owner_id"] = post["source_id"]
        post["id"] = post["post_id"]
    # result_posts = takewhile(lambda post: post["date"] >= time_begin, result_posts)
    result_posts = filter(
        lambda post: time_begin <= post["date"] < time_end,
        result_posts
    )
    result_posts = _remove_duplicates_posts_and_sort(result_posts)
    return result_posts


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


def _get_sorted_posts(posts):
    return sorted(
        posts,
        key=lambda post: (post["date"], post["owner_id"], post["id"]),
        reverse=True
    )
