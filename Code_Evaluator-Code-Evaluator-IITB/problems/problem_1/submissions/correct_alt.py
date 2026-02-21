def two_sum(nums: list[int], target: int) -> list[int]:
    lookup = {}
    for index in range(len(nums)):
        remaining = target - nums[index]
        if remaining in lookup:
            return [lookup[remaining], index]
        lookup[nums[index]] = index
    return []
