if __name__ == '__main__':
    cmd = "scrapy crawl Naver -a start_date='2015-0%s-%s' -a end_date='2015-0%s-%s' &> tutorial/spiders/logs/log-2015-0%s-%s.log"
    commands = []

    month = 5
    day = 20
    while day <= 31:
        str_day = day
        if day < 10:
            str_day = '0%s' % day
        commands.append(cmd % (month, str_day, month, str_day, month, str_day))
        day += 1

    month = 6
    day = 1
    while day <= 30:
        str_day = day
        if day < 10:
            str_day = '0%s' % day
        commands.append(cmd % (month, str_day, month, str_day, month, str_day))
        day += 1

    month = 7
    day = 1
    while day <= 17:
        str_day = day
        if day < 10:
            str_day = '0%s' % day
        commands.append(cmd % (month, str_day, month, str_day, month, str_day))
        day += 1

    with open('run_crawler.sh', 'w') as f:
        for line in commands:
            f.write(line + "\n")
