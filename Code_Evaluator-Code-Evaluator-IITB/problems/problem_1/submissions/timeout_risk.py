def two_sum(nums: list[int], target: int) -> list[int]:
    results = []
    for i in range(len(nums)):
        for j in range(len(nums)):
            if i != j:
                total = 0
                for k in range(nums[i]):
                    total += 1
                for k in range(nums[j]):
                    total += 1
                if total == target:
                    results.append([i, j])
    if results:
        return results[0]
    return []
