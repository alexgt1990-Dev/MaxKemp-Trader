def add_volume_indicators(data):
    data["VOL_AVG20"] = data["Volume"].rolling(20).mean()
    data["REL_VOLUME"] = data["Volume"] / data["VOL_AVG20"]
    return data
