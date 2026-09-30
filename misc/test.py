from collections import Counter

def maxDistinct(nums, k):
    if not nums:
        return 0

    cnt = Counter(nums)
    vals = sorted(cnt)            # unique values, ascending
    stack = []                    # pending duplicates; top = largest = closest
    costs = []                    # cost of each possible new distinct value

    for i, v in enumerate(vals):
        # Extra copies of v need to move up to a free value
        stack.extend([v] * (cnt[v] - 1))

        # Free values are strictly between v and the next existing value
        # (unbounded after the last value)
        g = v + 1
        while stack and (i + 1 == len(vals) or g < vals[i + 1]):
            costs.append(g - stack.pop())   # increments to move top dup to g
            g += 1

    # Each placement adds exactly +1 distinct, so buy the cheapest first
    costs.sort()
    extra = 0
    for c in costs:
        if c > k:
            break
        k -= c
        extra += 1

    return len(vals) + extra


print(maxDistinct([5,2,1,1,5,6], 1))
