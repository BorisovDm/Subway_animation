import os
import pandas as pd


CIRCLE_LINES = ['Московское центральное кольцо', 'Кольцевая линия']


class Subway:

    def __init__(self, path=os.path.join('data', 'moscow.csv')):
        self.df = pd.read_csv(path)

        # boundaries of frame
        self.x_min, self.x_max = min(self.df['lon']), max(self.df['lon'])
        self.y_min, self.y_max = min(self.df['lat']), max(self.df['lat'])

        # year values
        self.years = sorted(self.df['year'].unique())

        # lines names values
        self.lines_names = self.df['line'].unique()

        # subway lines
        self.lines = [SubwayLine(self.df[self.df['number'] == line_number].T.to_dict().values())\
                      for line_number in self.df['number'].unique()]

    def get_stations_by_year_filter(self, year):
        markers = [line.get_stations_by_year_filter(year) for line in self.lines]
        lines = [line.get_edges_by_year_filter(year) for line in self.lines]
        markers.extend(lines)

        return markers


class SubwayLine:

    def __init__(self, stations_description):
        self.stations = [SubwayStation(**station) for station in stations_description]
        self.stations.sort(key=lambda x: x.order)

        self.color = self.stations[0].color
        self.name = self.stations[0].line
        self.number = self.stations[0].number
        # self.edges = [(st_1.get_geo(), st_2.get_geo()) for st_1, st_2 in zip(self.stations, self.stations[1:])]

    def _stations_year_filter(self, year):
        stations_indexes = [idx for idx, station in enumerate(self.stations) if station.year <= year]
        return stations_indexes

    def get_edges_by_year_filter(self, year):
        stations_indexes = self._stations_year_filter(year)
        lon_list, lat_list = list(), list()

        if len(stations_indexes) != 0:
            # add empty value to avoid skipping None values in append method
            lon_list, lat_list = [-9999], [-9999]

            for idx, station in enumerate(self.stations):
                flag = (idx >= stations_indexes[0]) and (idx <= stations_indexes[-1])
                lon_list.append(station.lon if flag else None)
                lat_list.append(station.lat)

            lon_list.pop(0)
            lat_list.pop(0)

            if self.name in CIRCLE_LINES and len(stations_indexes) == len(self.stations):
                lon_list.append(lon_list[0])
                lat_list.append(lat_list[0])

        lines_dict = {
            'x': lon_list,
            'y': lat_list,
            'mode': 'lines',
            'line': dict(width=1, color=self.color),
            'legendgroup': '{}({})'.format(self.name, self.number),
            'name': self.name,
            'showlegend': False
        }

        return lines_dict

    def get_stations_by_year_filter(self, year):
        lat_list = [station.lat for station in self.stations]
        lon_list = [station.lon for station in self.stations]
        names_list = [station.name for station in self.stations]
        stations_indexes = self._stations_year_filter(year)

        markers_dict = {
            'mode': 'markers',
            'name': self.name,
            'legendgroup': '{}({})'.format(self.name, self.number),
            'text': names_list,
            'hoverinfo': 'text',
            'x': lon_list,
            'y': lat_list,
            'marker': dict(color=self.color),
            'selectedpoints': stations_indexes,
        }

        return markers_dict


class SubwayStation:

    def __init__(self, lat, lon, station, year, line, order, line_color, number, **kwargs):
        self.lat = lat
        self.lon = lon
        self.name = station
        self.year = year
        self.line = line
        self.order = order
        self.color = line_color
        self.number = number
