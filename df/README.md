# Расшифровка датафреймов

```main_data, values_data, order_data = l_parser.parse_train_sample(0, 30, filter_crawlers=True, parse_ua=True)```

```main_bot_data, values_bot_data, order_bot_data = l_test_parser.parse_bot_sample(30, 60, 60, 90, filter_crawlers=True, parse_ua=True)``` Без индексов у main_bot_data

```main2_data, values2_data, order2_data = l_parser.parse_train_sample(30, 40, filter_crawlers=True, parse_ua=True)```

```main2_bot_data, values2_bot_data, order2_bot_data = l_test_parser.parse_bot_sample(50, 60, 40, 50, filter_crawlers=True, parse_ua=True)``` Без индексов у 