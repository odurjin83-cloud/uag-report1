from test_app import ApplicationTests, connection

class CompletionTests(ApplicationTests):
    def test_unapproved_completion_updates_to_100(self):
        self.login()
        response=self.post('/complete/4',{'task_result':'Дуусгасан үр дүн'})
        self.assertEqual(response.status_code,302)
        with connection(self.path) as db:
            self.assertEqual(db.execute('SELECT progress,status FROM reports WHERE id=4').fetchone(),('100%','submitted'))
        self.assertEqual(self.post('/complete/4',{'task_result':'Давтах'}).status_code,409)

    def test_approved_completion_review_return_resubmit(self):
        with connection(self.path) as db: db.execute("UPDATE reports SET status='approved' WHERE id=4")
        self.login()
        self.assertEqual(self.post('/complete/1',{'task_result':'Бусдын ажил'}).status_code,404)
        self.assertEqual(self.post('/complete/4',{'task_result':'Нэмэлт үр дүн'}).status_code,302)
        self.assertEqual(self.post('/complete/4',{'task_result':'Давтах'}).status_code,409)
        with connection(self.path) as db:
            self.assertEqual(db.execute('SELECT progress,status FROM reports WHERE id=4').fetchone(),('75%','approved'))
            ident=db.execute('SELECT id FROM report_revisions').fetchone()[0]
        self.assertEqual(self.client.get('/reviews').status_code,403)
        self.login('boss@example.com')
        self.assertEqual(self.post(f'/reviews/{ident}',{'action':'return','note':'Үр дүнг тодруулах'}).status_code,302)
        self.login()
        self.assertIn('Үр дүнг тодруулах',self.client.get('/complete/4').get_data(as_text=True))
        self.assertEqual(self.post('/complete/4',{'task_result':'Бүрэн тодорхой үр дүн'}).status_code,302)
        self.login('boss@example.com')
        with connection(self.path) as db: ident=db.execute("SELECT id FROM report_revisions WHERE status='pending'").fetchone()[0]
        self.assertEqual(self.post(f'/reviews/{ident}',{'action':'approve'}).status_code,302)
        with connection(self.path) as db:
            self.assertEqual(db.execute('SELECT progress,status,task_result FROM reports WHERE id=4').fetchone(),('100%','approved','Бүрэн тодорхой үр дүн'))
            self.assertEqual(db.execute('SELECT COUNT(*) FROM report_revisions').fetchone()[0],2)
        self.assertEqual(self.post(f'/reviews/{ident}',{'action':'approve'}).status_code,409)

    def test_dashboard_scope(self):
        self.login()
        html=self.client.get('/dashboard'+self.query+'&dept=ЗОНХХэлтэс').get_data(as_text=True)
        self.assertIn('private-3',html)
        self.assertNotIn('private-0',html)
        self.assertEqual(self.client.get('/?incomplete=1').status_code,200)
