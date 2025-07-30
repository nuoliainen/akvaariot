# Akvaariosovellus

Sovellus, jolla voit pitää kirjaa akvarioistasi ja niiden asukkaista, sekä selata muiden ihmisten lisäämiä akvaarioita.


## Ominaisuudet

- [x] Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
- [x] Käyttäjä pystyy lisäämään sovellukseen akvaarioita. Lisäksi käyttäjä pystyy muokkaamaan ja poistamaan lisäämiään akvaarioita.
- [ ] Akvaarioon voi lisätä asukkeja, laitteistoa ja muuta tietoa sekä kuvia.
- [x] Käyttäjä näkee sovellukseen lisätyt akvaariot. Käyttäjä näkee sekä itse lisäämänsä että muiden käyttäjien lisäämät akvaariot.
- [x] Käyttäjä pystyy etsimään omia ja muiden akvaarioita hakusanan perusteella.
- [ ] Käyttäjä pystyy etsimään/rajaamaan omia ja muiden akvaariota lajin, koon jne. perusteella.
- [x] Sovelluksessa on käyttäjäsivut, jotka näyttävät jokaisesta käyttäjästä tilastoja (akvaarioiden lukumäärä, lajien ja yksilöiden lukumäärä jne.) ja käyttäjän lisäämät akvaariot.
- [ ] Käyttäjä pystyy valitsemaan akvaariolle yhden tai useamman luokittelun (esim. suunnitelma/oikea akvaario, makea/merivesi, trooppinen/viileä, biotooppi, blackwater, lajiakvaario jne.).
- [ ] Käyttäjä pystyy kommentoimaan tai lisäämään jonkin reaktion omiin ja muiden käyttäjien akvaarioihin.


## Sovelluksen käynnistäminen

*(Windows)*  
Kloonaa repositorio komennolla `git clone` https://github.com/nuoliainen/akvaariot tai [lataa ZIP-tiedosto](https://github.com/nuoliainen/akvaariot/archive/refs/heads/main.zip) ja pura kansio. Tuplaklikkaa RUN.bat tiedostoa tai syötä komentoja manuaalisesti seuraavan kuvauksen mukaisesti: RUN.bat tiedosto luo virtuaaliympäristön komennolla `python -m venv venv` jos sitä ei vielä ole. Virtuaaliympäristö aktivoidaan komennolla `call venv\Scripts\activate`. Jos virtuaaliympäristö vasta luotiin, asennetaan Flask komennolla `pip install flask`. Tietokanta luodaan komennolla `sqlite3 database.db < schema.sql` jos sitä ei vielä ole. Sen jälkeen suoritetaan komento `flask run`, jolloin sovelluksen pitäisi toimia selaimella osoitteessa http://127.0.0.1:5000/.


## Sovelluksen testaaminen

1. Käynnistä sovellus (yllä olevien ohjeiden mukaisesti)
2. Avaa selain ja siirry osoitteeseen http://127.0.0.1:5000
3. Luo uusi käyttäjätunnus valitsemalla *Luo tunnus*
4. Kirjaudu sisään ja käytä sovelluksen toimintoja:
   - Lisää uusia akvaarioita
   - Muokkaa akvaarioita tai poista niitä
   - Kokeile hakutoimintoa kirjoittamalla jokin hakusana
5. Kirjaudu ulos