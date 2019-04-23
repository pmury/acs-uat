import unittest
import pprint
import os

from csextensions.helpers.helpers import *
from csextensions.helpers.stage import Stage
from csextensions.helpers.randominfrastructure import RandomInfrastructure
from csextensions.primitives.zone import Zone
from csextensions.primitives.network import Network
from csextensions.primitives.vpc import VPC
from csextensions.primitives.tags import Tags


class TestTags(unittest.TestCase):

    @classmethod
    def setUpClass(self):

        stage = Stage()
        self.cs = stage.get_cs()
        self.natnework_id = None

        n = Network(self.cs)
        v = VPC(self.cs)
        z = Zone(self.cs)

        lbofferingid =v.getVpcOfferingId(vpcname="Default VPC offering")
        r = RandomInfrastructure(self.cs)
        randomzone = r.random_zone_name()
        self.zoneid=z.getZoneId(randomzone)

        vpcid = v.createVPC(cidr = "192.168.1.0/24", displaytext = "My VPC", name = "test_tags_vpc", vpcofferingid = lbofferingid, zoneid = self.zoneid)
        self.vpcid = vpcid
        assert v.vpcExists("test_tags_vpc")




    @classmethod
    def tearDownClass(self):
        v = VPC(self.cs)
        n = Network(self.cs)
        if self.natnework_id is not None:
            n.delete_network(id = self.natnework_id)

        if v.vpcExists("test_tags_vpc"):
                v.deleteVPC(id = self.vpcid)



    def test_tags_network_acl(self):

        v = VPC(self.cs)
        acl_list_id = v.createNetworkACLList(name = "acl_tag_test", vpcid = self.vpcid )

        acl_id = v.createNetworkACL(aclid = acl_list_id, cidrlist="0.0.0.0/0", traffictype="ingress", action = "allow", protocol = "tcp",  startport="80",endport="80", icmptype="", icmpcode="")

        print("tag ACL - NetworkAcl")
        tagsresult = self.cs.createTags(resourceids=[acl_id], resourcetype="NetworkAcl", tags=[{"key": "foo", "value": "bar"},{"key": "bar", "value": "baz"}])
        asj = AsyncJob(self.cs, tagsresult['jobid'])
        assert asj.isSuccessful() == True

        result = self.cs.listTags(resourceid=acl_id)


    def test_tags_network_acl2(self):

        v = VPC(self.cs)
        acl_list_id = v.createNetworkACLList(name = "acl_tag_test", vpcid = self.vpcid )

        acl_id = v.createNetworkACL(aclid = acl_list_id, cidrlist = "0.0.0.0/0", traffictype = "ingress", action = "allow", protocol = "tcp",  startport = "80",endport = "80", icmptype="", icmpcode="")

        print("tag ACL - NetworkACL")
        tagsresult = self.cs.createTags(resourceids=[acl_id], resourcetype="NetworkACL", tags=[{"key": "foo", "value": "bar"},{"key": "bar", "value": "baz"}])
        asj = AsyncJob(self.cs, tagsresult['jobid'])
        assert asj.isSuccessful() == True

        result = self.cs.listTags(resourceid = acl_id)

    def test_tags_network_acllist(self):

        v = VPC(self.cs)

        acl_list_id = v.createNetworkACLList(name = "acl_tag_test", vpcid = self.vpcid )

        acl_id = v.createNetworkACL(aclid = acl_list_id, cidrlist = "0.0.0.0/0", traffictype="ingress", action = "allow", protocol = "tcp",  startport ="80",endport = "80", icmptype ="", icmpcode="")

        print("tag ACL List - NetworkACL")
        tagsresult = self.cs.createTags(resourceids = [acl_list_id], resourcetype="NetworkACLList", tags=[{"key": "foo", "value": "bar"},{"key": "bar", "value": "baz"}])
        asj = AsyncJob(self.cs,tagsresult['jobid'])
        assert asj.isSuccessful() is True

        result = self.cs.listTags(resourceid = acl_id)




    def test_tags_network_nat(self):

        n = Network(self.cs)
        v = VPC(self.cs)
        z = Zone(self.cs)
        lbofferingid =v.getVpcOfferingId(vpcname="Default VPC offering")

        offering = n.getNetworkOfferingId(name="NAT")
        NAT_Network = n.create_network(name = "mynatnetwork_tagtest", displaytext ="Some NAT Test Network", networkofferingid = offering, zoneid = self.zoneid)
        self.natnework_id = NAT_Network['id']

        assert(n.network_exists(id = NAT_Network['id']))

        tagsresult = self.cs.createTags(resourceids=[NAT_Network['id']], resourcetype="Network", tags=[{"key": "foo", "value": "bar"},{"key": "furb", "value": "barz"}])
        asj = AsyncJob(self.cs, tagsresult['jobid'])
        assert asj.isSuccessful() is True

        result = self.cs.listTags(resourceid=NAT_Network['id'])

        c = 0

        for t in result['tag']:
            if t['key'] == 'foo':
                assert(t['value'] == 'bar')
                c = c+1

            if t['key'] == 'furb':
                assert(t['value'] == 'barz')
                c = c+1

        assert c==2

        n.delete_network(id = NAT_Network['id'])
