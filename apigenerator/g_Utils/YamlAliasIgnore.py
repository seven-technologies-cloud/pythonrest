import yaml


class NoAliasDumper(yaml.Dumper):
    def ignore_aliases(self, data):
        return True
