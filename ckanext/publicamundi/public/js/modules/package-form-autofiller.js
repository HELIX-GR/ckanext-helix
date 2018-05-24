
this.ckan.module('package-form-autofiller', function ($, _) {
    
  return {
    
    samples: {
        "resource-form": [
            {
                'url': 'http://example.com/res/1',
                'description': 'A very interesting example',
                'name': 'A web page example',
                'format': 'HTML',
            },
            {
                'url': window.location.origin + '/samples/1.csv',
                'description': 'A quite interesting CSV example',
                'name': 'A CSV example',
                'format': 'CSV',
            },
            {
                'url': window.location.origin + '/samples/1.rdf',
                'description': 'A remarkable RDF example',
                'name': 'An RDF example',
                'format': 'RDF',
            },

        ],
        "package-form": [
            {
                'title': 'Hello Foo 1',
                'name': 'hello-foo-1',
                'dataset_type': 'foo',
                'notes': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do ' +
                         'eiusmod tempor incididunt ut labore et dolore magna aliqua.',
                'tags': ['hello-world', 'foo', 'lorem-ipsum'],
                'license': 'gfdl',
                'version': '1.0.1',
                'url': 'http://example.com/datasets/foo/1',
                'author': 'Λαλάκης',
                'author_email': 'lalakis@example.com',
		'publisher': 'Λαλάκης',
		'identifier': '10.12449/foo',
		'license_uri': 'http://creativecommons.org/licenses/by/3.0/de/deed.en',
        'creator_affiliation': 'IMSI',
        'contributor_name': 'Mitsos',
        'creator_name': 'Jim',
        'language': 'Greek',
        'publication_year': 2002,
        'optional_title': 'Ελληνικός τίτλος1',
        'optional_notes': 'Ελληνική περιγραφη αδςδςαννδνς αςδαδς1'
            },
            {
                'title': 'Hello Foo 2',
                'name': 'hello-foo-2',
                'dataset_type': 'foo',
                'notes': 'I am another _Foo_ package!',
                'tags': ['hello-world', 'foo', 'test'],
                'license': 'cc-by',
                'version': '1.0.2',
                'url': 'http://example.com/datasets/foo/2',
                'author': 'Φουφουτος',
                'author_email': 'foofootos@example.com',
		'publisher': 'Φούφουτος',
		'identifier': '10.38449/foo',
		'license_uri': 'http://creativecommons.org/licenses/by/3.0/de/deed.en',
        'creator_affiliation': 'IMSI',
        'contributor_name': 'Takis',
        'creator_name': 'Bob',
        'language': 'English',
        'publication_year': 2003,
        'optional_title': 'Ελληνικός τίτλος2',
        'optional_notes': 'Ελληνική περιγραφη αδςδςαννδνς αςδαδς2'
            },    
            {
                'title': 'Hello Inspire 1',
                'name': 'hello-inspire-1',
                'dataset_type': 'inspire',
                'notes': 'I am another _INSPIRE_ package!',
                'tags': ['hello-world', 'inspire', 'test'],
                'license': 'cc-by',
                'version': '1.0.1',
                'url': 'http://example.com/datasets/inspire/1',
                'author': 'Φουφουτος',
                'author_email': 'inspired@example.com',
		'publisher': 'Φούφουτος',
		'identifier': '10.38449/foo',
		'license_uri': 'http://creativecommons.org/licenses/by/3.0/de/deed.en',
        'creator_affiliation': 'IMSI',
        'contributor_name': 'Makis',
        'creator_name': 'Mark',
        'language': 'greek',
        'publication_year': 2004,
        'optional_title': 'Ελληνικός τίτλος3',
        'optional_notes': 'Ελληνική περιγραφη αδςδςαννδνς αςδαδς3'
            }, 
            {
                'title': 'Hello CKAN 1',
                'name': 'hello-ckan-1',
                'dataset_type': 'ckan',
                'notes': 'I am a plain _CKAN_ package!',
                'tags': ['hello-world', 'ckan', 'test'],
                'license': 'cc-by',
                'version': '1.0.4',
                'url': 'http://example.com/datasets/ckan/1',
                'author': 'Φουφουτος',
                'author_email': 'ckaner@example.com',
		'publisher': ' Φούφουτος',
		'identifier': '10.38449/foo',
		'license_uri': 'http://creativecommons.org/licenses/by/3.0/de/deed.en',
        'creator_affiliation': 'IMSI',
        'contributor_name': 'Mitsos',
        'creator_name': 'George',
        'language': 'english',
        'publication_year': 2006,
        'optional_title': 'Ελληνικός τίτλος4',
        'optional_notes': 'Ελληνική περιγραφη αδςδςαννδνς αςδαδς4'
            },
        ],
    },
    
    _sample: function(formid) 
    {
        var samples = this.samples[formid]
        var i = Math.floor(Math.random() * 1e4) % samples.length
        return samples[i]
    },
    
    options: {
        formid: 'package-form',
    },

    initialize: function() 
    {
        var module = this
        var el = this.el

        var $form = $('#' + this.options.formid)
        var $form2 = $('#' + this.options.formid + 'foo-fields-group-creator')    
        
        switch (this.options.formid) {
            default:
            case 'package-form':
                {
                    this.el.on('click', function() {
                        data = module._sample(module.options.formid)
                        $form.find('#field-title').val(data['title'])
                        $form.find('#field-dataset_type').select2('val', data['dataset_type'])
                        $form.find('#field-notes').val(data['notes'])
                        $form.find('#field-tags').select2('val', data['tags'])
                        $form.find('#field-license').select2('val', data['license'])
                        $form.find('#field-version').val(data['version'])
                        $form.find('#field-url').val(data['url'])
                        $form.find('#field-author').val(data['author'])
                        $form.find('#field-author-email').val(data['author_email'])
			$form.find('#field-publisher').val(data['publisher'])
			$form.find('#field-identifier').val(data['identifier'])
			$form.find('#field-license-uri').val(data['license_uri'])
            $form.find('#input-foo\\.creator\\.creator_affiliation').val(data['creator_affiliation'])
            $form.find('#input-foo\\.creator\\.creator_name').val(data['creator_name'])
            $form.find('#input-foo\\.contributor\\.contributor_name').val(data['contributor_name'])
            $form.find('#input-foo\\.publication_info\\.publication_year').val(data['publication_year'])
            $form.find('#input-foo\\.language').select2('val', data['language'])
            $form.find('#input-foo\\.optional_title').val(data['optional_title'])
            $form.find('#input-foo\\.optional_description').val(data['optional_notes'])
                        return false
                    })
                    this.el.css('margin', '0px 5px')
                    this.el.insertBefore($form.find('button.btn-primary[name="save"]').first())
                    this.el.show()
                }
                break;
            case 'resource-form':
                {
                    this.el.on('click', function() {
                        data = module._sample(module.options.formid)
                        $form.find("label[for='field-image-upload']").parent().find('.btn:visible:eq(1)').click()
                        $form.find('#field-image-url').val(data['url'])
                        $form.find('#field-name').val(data['name'])
                        $form.find('#field-description').val(data['description'])
                        $form.find('#field-format').select2('val', data['format'])
                        return false
                    })
                    this.el.css('margin', '0px 5px')
                    this.el.insertBefore($form.find('button.btn-primary[name="save"]').first())
                    this.el.show()
                }
                break;
        }

        window.console.debug('Initialized module: package-form-autofiller')
    },
    teardown: function() { 
        window.console.debug('Tearing down module: package-form-autofiller')
    },
  }
});

