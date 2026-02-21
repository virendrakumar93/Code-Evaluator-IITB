def two_sum(nums: list[int], target: int) -> list[int]:
    d={}
    for x in range(len(nums)):
        v=target-nums[x]
        if v in d:return[d[v],x]
        d[nums[x]]=x
    return[]
