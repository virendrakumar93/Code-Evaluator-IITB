def two_sum(nums: list[int], target: int) -> list[int]:
    num_set = set(nums)
    for i, num in enumerate(nums):
        complement = target - num
        if complement in num_set and complement != num:
            for j in range(i + 1, len(nums)):
                if nums[j] == complement:
                    return [i, j]
    return []
