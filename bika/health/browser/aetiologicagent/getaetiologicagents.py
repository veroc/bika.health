from bika.lims.browser import BrowserView
from bika.lims.permissions import *
from operator import itemgetter
import json
import plone


class ajaxGetAetiologicAgents(BrowserView):
    """ Aetologic Agents from site setup
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        title = 'title' in self.request and self.request['title'] or ''
        uid = 'uid' in self.request and self.request['uid'] or ''
        searchTerm = (len(title) == 0 and 'searchTerm' in self.request) and self.request['searchTerm'].lower() or title.lower()
        page = 'page' in self.request and self.request['page'] or 1
        nr_rows = 'rows' in self.request and self.request['rows'] or 10
        sord = 'sord' in self.request and self.request['sord'] or 'asc'
        sidx = 'sidx' in self.request and self.request['sidx'] or 'Title'
        rows = []

        # lookup objects from ZODB
        agents = self.bika_setup_catalog(portal_type='AetiologicAgent',
                                         inactive_state='active')
        if agents and searchTerm:
            agents = [agent for agent in agents if agent.Title.lower().find(searchTerm) > -1
                      or agent.Description.lower().find(searchTerm) > -1]
        for agent in agents:
            agent = agent.getObject()
            if (len(title) > 0 and agent.Title() == title):
                rows.append({'Title': agent.Title(),
                             'Description': agent.Description(),
                             'AgentUID': agent.UID()})
            elif len(uid) > 0 and agent.UID() == uid:
                rows.append({'Title': agent.Title(),
                             'Description': agent.Description(),
                             'AgentUID': agent.UID()})
            elif len(title) == 0 and len(uid) == 0:
                rows.append({'Title': agent.Title(),
                             'Description': agent.Description(),
                             'AgentUID': agent.UID()})

        rows = sorted(rows, cmp=lambda x, y: cmp(x.lower(), y.lower()), key=itemgetter(sidx and sidx or 'Title'))
        if sord == 'desc':
            rows.reverse()
        pages = len(rows) / int(nr_rows)
        pages += divmod(len(rows), int(nr_rows))[1] and 1 or 0
        ret = {'page': page,
               'total': pages,
               'records': len(rows),
               'rows': rows[(int(page) - 1) * int(nr_rows): int(page) * int(nr_rows)]}

        return json.dumps(ret)
