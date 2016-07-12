from django import forms


class CrawlerForm(forms.Form):
    keywords_phrase = forms.CharField(label='Enter keywords')

    def clean(self):
        keywords_phrase = self.cleaned_data.get('keywords_phrase')
        if not keywords_phrase:
            raise forms.ValidationError('Keywords field is required.')
        return self.cleaned_data