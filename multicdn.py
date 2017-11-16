###################################################################
#  Manipulate multi cdn / multi bucket configuration
#
###################################################################
import os
import json
import yaml

debug=os.environ.get('debug', False)
config_file=os.environ.get('config_file', 'multicdn.config.yml')

class Multicdn:
    # ..................................................................................................
    def __init__(self, buckets_configuration='cdnDomains', cdn_configurations='cdnConfigurations', filename=config_file):
        self.buckets_configuration=buckets_configuration
        self.filename=filename
        self.cdn_configurations = cdn_configurations

        return None

    # ..................................................................................................
    def getConf(self, buckets_configuration=None, filename=None):
        # domain: the top level yaml key, NOT an internet domain
        buckets_configuration = buckets_configuration if buckets_configuration else self.buckets_configuration
        filename = filename if filename else self.filename
        assert os.path.exists(filename), "File %r does not exist" % (filename)
        yml = yaml.load(open(filename))
        assert buckets_configuration in yml , "Key %r is not in root of file %r" % (buckets_configuration, filename)
        cdn_list = yml[buckets_configuration]
        cdn_configurations =  self.cdn_configurations
        assert cdn_configurations in yml, "Key %r is not in root of file %r" % (cdn_configurations, filename)
        domain_map = {}
        for cdn in cdn_list:
            default_platform = yml[cdn_configurations].get(cdn, {}).get('platform' , None)
            # bucketmap = {something['Name']:something['Value'] for something in cdn_item['Attributes']}
            for bucket_name, host_config_list in cdn_list[cdn].iteritems():
                if bucket_name not in domain_map:
                    domain_map[bucket_name] = {}
                if cdn not in domain_map[bucket_name]:
                    domain_map[bucket_name][cdn] = {} # host_config_list
                for host_config in host_config_list:
                    host_platform = host_config.get('platform', default_platform)
                    if host_platform not in domain_map[bucket_name][cdn]:
                        domain_map[bucket_name][cdn][host_platform]=[]
                    domain_map[bucket_name][cdn][host_platform].append(host_config)

        return domain_map


    # ..................................................................................................
    def getCDNConf(self, cdn_configurations=None, filename=None):
        # domain: the top level yaml key, NOT an internet domain
        cdn_configurations = cdn_configurations if cdn_configurations else self.cdn_configurations
        filename = filename if filename else self.filename
        assert os.path.exists(filename), "File %r does not exist" % (filename)
        yml = yaml.load(open(filename))
        assert cdn_configurations in yml, "Key %r for CDN configuration is not in root of file %r" % (cdn_configurations, filename)
        cdn_configurations_map = yml[cdn_configurations]
        return cdn_configurations_map


if __name__=='__main__':
    s = Multicdn()
    x = s.getConf()
    print "this is local", json.dumps(x)
