import unittest
import time
from csextensions.primitives.vpc import VPC
from csextensions.primitives.template import Template
from csextensions.fixtures.vm_vpc import VM_VPC
from csextensions.primitives.zone import Zone
from csextensions.helpers.randominfrastructure import RandomInfrastructure


class TestStress(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        pass

    @classmethod
    def tearDownClass(self):
        pass

    def test_template(self):

        fx = VM_VPC()

        Z = Zone(fx.cs)
        T = Template(fx.cs)
        zone = "Enterprise"
        zid = Z.getZoneId(zone)

        fxt = fx.get_fixture()
        fxt.update({"zone": {"id": zid, "name": zone}})

        template = "centos7.5"
        template_id = T.getTemplateId(name=template, zoneid=fxt['zone']['id'])

        fxt['vm'].update({"template": {"id": template_id, "name": template}})
        fxt['vpc']['offering']['name'] = 'Default VPC Offering (512MB)'
        fxt['vpc']['offering']['id'] = 'ef9262cc-2595-4aea-a35a-1bf3d1d23c99'

        fx.build()
        fxt = fx.get_fixture()

        r = fx.cs.listRouters(vpcid=fxt['vpc']['id'])
        print("VPR: %s" % r['router'][0])

        v = VPC(fx.cs)

        aclid = fxt['vpc']['acl']['id']

        ri = RandomInfrastructure(fx.cs)

        for port in range(10000, 10050):
            cidr_list = ri.random_cidr_list(350)

            print("create ACL with %s CIDRs for port %s" % (350, port))

            v.createNetworkACL(aclid=aclid, cidrlist=cidr_list,
                               traffictype="ingress", action="allow",
                               protocol="tcp", startport=port, endport=port,
                               icmptype="", icmpcode="")

            print("give VPR time to create iptables.")
            time.sleep(300)
