# -*- coding: utf-8 -*-
from parsers import riigiteataja_parse, rss_parse, ministry_parse, eurlex_parse


class Constant():
  def __init__(self, name, child_constants=None, values={}):
    self.name = name
    self.values = values
    self.child_constants = child_constants


class ConstantMixin(object):
  """
    Return property names of class and remove built-ins that start with '_'
  """
  @classmethod
  def get_class_properties(cls):
    return [prop for prop in cls.__dict__.keys() if prop[0] != '_']

  @classmethod
  def get_constants(cls):
    return [getattr(cls, prop) for prop in cls.get_class_properties()]


class Abbreviations(ConstantMixin):
  AVRS = Constant('AVRS', values={'long_name': 'Abieluvararegistri seadus'})
  APolS = Constant('APolS', values={'long_name': 'Abipolitseiniku seadus'})
  AdvS = Constant('AdvS', values={'long_name': 'Advokatuuriseadus'})
  AMVS = Constant('AMVS', values={'long_name': 'Alaealise mõjutusvahendite seadus'})
  ATKEAS = Constant('ATKEAS', values={'long_name': 'Alkoholi-, tubaka-, kütuse- ja elektriaktsiisi seadus'})
  AS = Constant('AS', values={'long_name': 'Alkoholiseadus'})
  AUS = Constant('AÜS', values={'long_name': 'Ametiühingute seadus'})
  ASeS = Constant('ASeS', values={'long_name': 'Arenguseire seadus'})
  ArhS = Constant('ArhS', values={'long_name': 'Arhiiviseadus'})
  ATSS = Constant('ATSS', values={'long_name': 'Asendustäitmise ja sunniraha seadus'})
  AUA = Constant('AÜA', values={'long_name': 'Asjaajamiskorra ühtsed alused'})
  AOS = Constant('AÕS', values={'long_name': 'Asjaõigusseadus'})
  AOSRS = Constant('AÕSRS', values={'long_name': 'Asjaõigusseaduse rakendamise seadus'})
  AOKS = Constant('AÕKS', values={'long_name': 'Atmosfääriõhu kaitse seadus'})
  AudS = Constant('AudS', values={'long_name': 'Audiitortegevuse seadus'})
  AutOS = Constant('AutÕS', values={'long_name': 'Autoriõiguse seadus'})
  AutoVS = Constant('AutoVS', values={'long_name': 'Autoveoseadus'})
  AvTS = Constant('AvTS', values={'long_name': 'Avaliku teabe seadus'})
  ATS = Constant('ATS', values={'long_name': 'Avaliku teenistuse seadus'})
  BS = Constant('BS', values={'long_name': 'Biotsiidiseadus'})
  EAFS = Constant('EAFS', values={'long_name': 'Eesti Arengufondi seadus'})
  HKS = Constant('HKS', values={'long_name': 'Eesti Haigekassa seadus'})
  KultKS = Constant('KultKS', values={'long_name': 'Eesti Kultuurkapitali seadus'})
  ELS = Constant('ELS', values={'long_name': 'Eesti lipu seadus'})
  EPS = Constant('EPS', values={'long_name': 'Eesti Panga seadus'})
  ERRS = Constant('ERRS', values={'long_name': 'Eesti Rahvusraamatukogu seadus'})
  ERHS = Constant('ERHS', values={'long_name': 'Eesti Rahvusringhäälingu seadus'})
  ELTTS = Constant('ELTTS', values={'long_name': 'Eestisse lähetatud töötajate töötingimuste seadus'})
  TAS = Constant('TAS', values={'long_name': 'Eesti Teaduste Akadeemia seadus'})
  ETHS = Constant('ETHS', values={'long_name': 'Eesti territooriumi haldusjaotuse seadus'})
  OkupS = Constant('OkupS', values={'long_name': 'Eestit okupeerinud riikide julgeolekuorganite või relvajõudude luure - või vastuluureorganite teenistuses olnud või nendega koostööd teinud isikute arvelevõtmise ja avalikustamise korra seadus'})
  HaS = Constant('HaS', values={'long_name': 'Eesti Vabariigi haridusseadus'})
  ORAS = Constant('ORAS', values={'long_name': 'Eesti Vabariigi omandireformi aluste seadus'})
  PS = Constant('PS', values={'long_name': 'Eesti Vabariigi põhiseadus'})
  PSRS = Constant('PSRS', values={'long_name': 'Eesti Vabariigi põhiseaduse rakendamise seadus'})
  PSTS = Constant('PSTS', values={'long_name': 'Eesti Vabariigi põhiseaduse täiendamise seadus'})
  EVKS = Constant('EVKS', values={'long_name': 'Eesti väärtpaberite keskregistri seadus'})
  EhS = Constant('EhS', values={'long_name': 'Ehitusseadustik'})
  EhSRS = Constant('EhSRS', values={'long_name': 'Ehitusseadustiku ja planeerimisseaduse rakendamise seadus'})
  EUTS = Constant('EUTS', values={'long_name': 'E-identimise ja e-tehingute usaldusteenuste seadus'})
  ERTS = Constant('ERTS', values={'long_name': 'Ekspordi riikliku tagamise seadus'})
  ES = Constant('ES', values={'long_name': 'Elamuseadus'})
  ElatisAS = Constant('ElatisAS', values={'long_name': 'Elatisabi seadus'})
  ELTS = Constant('ELTS', values={'long_name': 'Elektrituruseadus'})
  ESS = Constant('ESS', values={'long_name': 'Elektroonilise side seadus'})
  EES = Constant('EES', values={'long_name': 'Eluruumide erastamise seadus'})
  EnKS = Constant('EnKS', values={'long_name': 'Energiamajanduse korralduse seadus'})
  EKS = Constant('EKS', values={'long_name': 'Erakonnaseadus'})
  EraKS = Constant('EraKS', values={'long_name': 'Erakooliseadus'})
  ErSS = Constant('ErSS', values={'long_name': 'Erakorralise seisukorra seadus'})
  ELRKS = Constant('ELRKS', values={'long_name': 'Erastamisest laekuva raha kasutamise seadus'})
  ErS = Constant('ErS', values={'long_name': 'Erastamisseadus'})
  EAS = Constant('EAS', values={'long_name': 'Etendusasutuse seadus'})
  ETS = Constant('ETS', values={'long_name': 'Ettevõtluse toetamise ja laenude riikliku tagamise seadus'})
  ELKS = Constant('ELKS', values={'long_name': 'Euroopa Liidu kodaniku seadus'})
  ELKTS = Constant('ELKTS', values={'long_name': 'Euroopa Liidu liikmesriigist ebaseaduslikult väljaviidud kultuuriväärtuste tagastamise seadus'})
  EMHUS = Constant('EMHÜS', values={'long_name': 'Euroopa Liidu Nõukogu määruse (EMÜ) nr 2137/85 «Euroopa majandushuviühingu kohta» rakendamise seadus'})
  SCEPS = Constant('SCEPS', values={'long_name': 'Euroopa Liidu Nõukogu määruse(EÜ) nr 1435/2003 «Euroopa ühistu(SCE) põhikirja kohta» rakendamise seadus'})
  SEPS = Constant('SEPS', values={'long_name': 'Euroopa Liidu Nõukogu määruse(EÜ) nr 2157/2001 «Euroopa äriühingu(SE) põhikirja kohta» rakendamise seadus'})
  ELUPS = Constant('ELÜPS', values={'long_name': 'Euroopa Liidu ühise põllumajanduspoliitika rakendamise seadus'})
  EKodAS = Constant('EKodAS', values={'long_name': 'Euroopa Parlamendi ja nõukogu määruse (EL) nr 211/2011 „Kodanikualgatuse kohta” rakendamise seadus'})
  ETKRS = Constant('ETKRS', values={'long_name': 'Euroopa Parlamendi ja nõukogu määruse(EÜ) nr 1082/2006 «Euroopa territoriaalse koostöö rühmituse (ETKR) kohta» rakendamise seadus'})
  EPVS = Constant('EPVS', values={'long_name': 'Euroopa Parlamendi valimise seadus'})
  FIS = Constant('FIS', values={'long_name': 'Finantsinspektsiooni seadus'})
  FELS = Constant('FELS', values={'long_name': 'Finantskriisi ennetamise ja lahendamise seadus'})
  GMMOKS = Constant('GMMOKS', values={'long_name': 'Geneetiliselt muundatud mikroorganismide suletud keskkonnas kasutamise seadus'})
  GMOVS = Constant('GMOVS', values={'long_name': 'Geneetiliselt muundatud organismide keskkonda viimise seadus'})
  GTKS = Constant('GTKS', values={'long_name': 'Geograafilise tähise kaitse seadus'})
  HKMS = Constant('HKMS', values={'long_name': 'Halduskohtumenetluse seadustik'})
  HKTS = Constant('HKTS', values={'long_name': 'Halduskoostöö seadus'})
  HMS = Constant('HMS', values={'long_name': 'Haldusmenetluse seadus'})
  HRS = Constant('HRS', values={'long_name': 'Haldusreformi seadus'})
  HasMMS = Constant('HasMMS', values={'long_name': 'Hasartmängumaksu seadus'})
  HasMS = Constant('HasMS', values={'long_name': 'Hasartmänguseadus'})
  HONTE = Constant('HÕNTE', values={'long_name': 'Hea õigusloome ja normitehnika eeskiri'})
  HLUS = Constant('HLÜS', values={'long_name': 'Hoiu-laenuühistu seadus'})
  HUS = Constant('HÜS', values={'long_name': 'Hooneühistuseadus'})
  HuviKS = Constant('HuviKS', values={'long_name': 'Huvikooli seadus'})
  HOS = Constant('HOS', values={'long_name': 'Hädaolukorra seadus'})
  ITVS = Constant('ITVS', values={'long_name': 'Individuaalse töövaidluse lahendamise seadus'})
  InfoTS = Constant('InfoTS', values={'long_name': 'Infoühiskonna teenuse seadus'})
  IGUS = Constant('IGUS', values={'long_name': 'Inimgeeniuuringute seadus'})
  IFS = Constant('IFS', values={'long_name': 'Investeerimisfondide seadus'})
  IKS = Constant('IKS', values={'long_name': 'Isikuandmete kaitse seadus'})
  ITDS = Constant('ITDS', values={'long_name': 'Isikut tõendavate dokumentide seadus'})
  JahiS = Constant('JahiS', values={'long_name': 'Jahiseadus'})
  JAS = Constant('JAS', values={'long_name': 'Julgeolekuasutuste seadus'})
  JaatS = Constant('JäätS', values={'long_name': 'Jäätmeseadus'})
  EMOES = Constant('EMOES', values={'long_name': 'Kaasomandis oleva elamu mõttelise osa erastamise seadus'})
  KaevS = Constant('KaevS', values={'long_name': 'Kaevandamisseadus'})
  KaLS = Constant('KaLS', values={'long_name': 'Kaitseliidu seadus'})
  KKS = Constant('KKS', values={'long_name': 'Kaitseväe korralduse seadus'})
  KVTS = Constant('KVTS', values={'long_name': 'Kaitseväeteenistuse seadus'})
  KVTRS = Constant('KVTRS', values={'long_name': 'Kaitseväeteenistuse seaduse rakendamise seadus'})
  KTKS = Constant('KTKS', values={'long_name': 'Kalandusturu korraldamise seadus'})
  KPS = Constant('KPS', values={'long_name': 'Kalapüügiseadus'})
  KalmS = Constant('KalmS', values={'long_name': 'Kalmistuseadus'})
  KarRS = Constant('KarRS', values={'long_name': 'Karistusregistri seadus'})
  KarS = Constant('KarS', values={'long_name': 'Karistusseadustik'})
  KarSRS = Constant('KarSRS', values={'long_name': 'Karistusseadustiku rakendamise seadus'})
  KasMS = Constant('KasMS', values={'long_name': 'Kasuliku mudeli seadus'})
  KaMS = Constant('KaMS', values={'long_name': 'Kaubamärgiseadus'})
  KMSK = Constant('KMSK', values={'long_name': 'Kaubandusliku meresõidu koodeks'})
  KMSS = Constant('KMSS', values={'long_name': 'Kaubandusliku meresõidu seadus'})
  KaubTS = Constant('KaubTS', values={'long_name': 'Kaubandustegevuse seadus'})
  KKutS = Constant('KKütS', values={'long_name': 'Kaugkütteseadus'})
  KeeleS = Constant('KeeleS', values={'long_name': 'Keeleseadus'})
  KBFIS = Constant('KBFIS', values={'long_name': 'Keemilise ja Bioloogilise Füüsika Instituudi seadus'})
  KemS = Constant('KemS', values={'long_name': 'Kemikaaliseadus'})
  KeJS = Constant('KeJS', values={'long_name': 'Keskkonnajärelevalve seadus'})
  KeHJS = Constant('KeHJS', values={'long_name': 'Keskkonnamõju hindamise ja keskkonnajuhtimissüsteemi seadus'})
  KeRS = Constant('KeRS', values={'long_name': 'Keskkonnaregistri seadus'})
  KeUS = Constant('KeÜS', values={'long_name': 'Keskkonnaseadustiku üldosa seadus'})
  KeSS = Constant('KeSS', values={'long_name': 'Keskkonnaseire seadus'})
  KeTS = Constant('KeTS', values={'long_name': 'Keskkonnatasude seadus'})
  KeVS = Constant('KeVS', values={'long_name': 'Keskkonnavastutuse seadus'})
  KiS = Constant('KiS', values={'long_name': 'Kiirgusseadus'})
  KindlTS = Constant('KindlTS', values={'long_name': 'Kindlustustegevuse seadus'})
  KAOKS = Constant('KAOKS', values={'long_name': 'Kinnisasja omandamise kitsendamise seadus'})
  KASVS = Constant('KASVS', values={'long_name': 'Kinnisasja sundvõõrandamise seadus'})
  KRS = Constant('KRS', values={'long_name': 'Kinnistusraamatuseadus'})
  KiKoS = Constant('KiKoS', values={'long_name': 'Kirikute ja koguduste seadus'})
  KodS = Constant('KodS', values={'long_name': 'Kodakondsuse seadus'})
  KoPS = Constant('KoPS', values={'long_name': 'Kogumispensionide seadus'})
  KoMS = Constant('KoMS', values={'long_name': 'Kohalike maksude seadus'})
  KOKS = Constant('KOKS', values={'long_name': 'Kohaliku omavalitsuse korralduse seadus'})
  KOVVS = Constant('KOVVS', values={'long_name': 'Kohaliku omavalitsuse volikogu valimise seadus'})
  KOFS = Constant('KOFS', values={'long_name': 'Kohaliku omavalitsuse üksuse finantsjuhtimise seadus'})
  KOLS = Constant('KOLS', values={'long_name': 'Kohaliku omavalitsuse üksuste liitude seadus'})
  KOUS = Constant('KOÜS', values={'long_name': 'Kohaliku omavalitsuse üksuste ühinemise soodustamise seadus'})
  KNS = Constant('KNS', values={'long_name': 'Kohanimeseadus'})
  KES = Constant('KES', values={'long_name': 'Kohtuekspertiisiseadus'})
  KS = Constant('KS', values={'long_name': 'Kohtute seadus'})
  KTS = Constant('KTS', values={'long_name': 'Kohtutäituri seadus'})
  KLS = Constant('KLS', values={'long_name': 'Kollektiivlepingu seadus'})
  KTTLS = Constant('KTTLS', values={'long_name': 'Kollektiivse töötüli lahendamise seadus'})
  KomPS = Constant('KomPS', values={'long_name': 'Kommertspandiseadus'})
  KonkS = Constant('KonkS', values={'long_name': 'Konkurentsiseadus'})
  KonS = Constant('KonS', values={'long_name': 'Konsulaarseadus'})
  KELS = Constant('KELS', values={'long_name': 'Koolieelse lasteasutuse seadus'})
  KooS = Constant('KooS', values={'long_name': 'Kooseluseadus'})
  KorS = Constant('KorS', values={'long_name': 'Korrakaitseseadus'})
  KVS = Constant('KVS', values={'long_name': 'Korruptsioonivastane seadus'})
  KrtS = Constant('KrtS', values={'long_name': 'Korteriomandi- ja korteriühistuseadus'})
  KOS = Constant('KOS', values={'long_name': 'Korteriomandiseadus'})
  KUS = Constant('KÜS', values={'long_name': 'Korteriühistuseadus'})
  KAVS = Constant('KAVS', values={'long_name': 'Krediidiandjate ja -vahendajate seadus'})
  KAS = Constant('KAS', values={'long_name': 'Krediidiasutuste seadus'})
  KrHS = Constant('KrHS', values={'long_name': 'Kriminaalhooldusseadus'})
  KrMS = Constant('KrMS', values={'long_name': 'Kriminaalmenetluse seadustik'})
  KrMSRS = Constant('KrMSRS', values={'long_name': 'Kriminaalmenetluse seadustiku rakendamise seadus'})
  KultVS = Constant('KultVS', values={'long_name': 'Kultuuriväärtuste väljaveo, ekspordi ja sisseveo seadus'})
  KTTS = Constant('KTTS', values={'long_name': 'Kunstiteoste tellimise seadus'})
  KVEKS = Constant('KVEKS', values={'long_name': 'Kunstliku viljastamise ja embrüokaitse seadus'})
  KutS = Constant('KutS', values={'long_name': 'Kutseseadus'})
  KutOS = Constant('KutÕS', values={'long_name': 'Kutseõppeasutuse seadus'})
  KRAPS = Constant('KRAPS', values={'long_name': 'Kõrgemate riigiteenijate ametipalkade seadus'})
  KMS = Constant('KMS', values={'long_name': 'Käibemaksuseadus'})
  LAOS = Constant('LAÕS', values={'long_name': 'Laeva asjaõigusseadus'})
  LaevaRS = Constant('LaevaRS', values={'long_name': 'Laeva lipuõiguse ja laevaregistrite seadus'})
  LasteKS = Constant('LasteKS', values={'long_name': 'Lastekaitseseadus'})
  LennS = Constant('LennS', values={'long_name': 'Lennundusseadus'})
  LepS = Constant('LepS', values={'long_name': 'Lepitusseadus'})
  LKindlS = Constant('LKindlS', values={'long_name': 'Liikluskindlustuse seadus'})
  LS = Constant('LS', values={'long_name': 'Liiklusseadus'})
  LKS = Constant('LKS', values={'long_name': 'Looduskaitseseadus'})
  LKVetJS = Constant('LKVetJS', values={'long_name': 'Loomade ja loomsete saadustega kauplemise ning nende impordi ja ekspordi seadus'})
  LoKS = Constant('LoKS', values={'long_name': 'Loomakaitseseadus'})
  LTTS = Constant('LTTS', values={'long_name': 'Loomatauditõrje seadus'})
  LLS = Constant('LLS', values={'long_name': 'Loovisikute ja loomeliitude seadus'})
  LMS = Constant('LMS', values={'long_name': 'Lõhkematerjaliseadus'})
  MPKS = Constant('MPKS', values={'long_name': 'Maaelu ja põllumajandusturu korraldamise seadus'})
  MGS = Constant('MGS', values={'long_name': 'Maagaasiseadus'})
  MHS = Constant('MHS', values={'long_name': 'Maa hindamise seadus'})
  MaaKatS = Constant('MaaKatS', values={'long_name': 'Maakatastriseadus'})
  MaaKS = Constant('MaaKS', values={'long_name': 'Maakorraldusseadus'})
  MaaMS = Constant('MaaMS', values={'long_name': 'Maamaksuseadus'})
  MaaParS = Constant('MaaParS', values={'long_name': 'Maaparandusseadus'})
  MaaPS = Constant('MaaPS', values={'long_name': 'Maapõueseadus'})
  MaaRKMOS = Constant('MaaRKMOS', values={'long_name': 'Maareformi käigus kasutusvaldusesse antud maa omandamise seadus'})
  MaaRS = Constant('MaaRS', values={'long_name': 'Maareformi seadus'})
  MPoS = Constant('MPõS', values={'long_name': 'Mahepõllumajanduse seadus'})
  MsuS = Constant('MsüS', values={'long_name': 'Majandustegevuse seadustiku üldosa seadus'})
  MVS = Constant('MVS', values={'long_name': 'Majandusvööndi seadus'})
  MERAS = Constant('MERAS', values={'long_name': 'Makseasutuste ja e-raha asutuste seadus'})
  MTVS = Constant('MTVS', values={'long_name': 'Maksualase teabevahetuse seadus'})
  MKS = Constant('MKS', values={'long_name': 'Maksukorralduse seadus'})
  MSS = Constant('MSS', values={'long_name': 'Meditsiiniseadme seadus'})
  MeeTS = Constant('MeeTS', values={'long_name': 'Meediateenuste seadus'})
  MPS = Constant('MPS', values={'long_name': 'Merealapiiride seadus'})
  MSOS = Constant('MSOS', values={'long_name': 'Meresõiduohutuse seadus'})
  MTooS = Constant('MTööS', values={'long_name': 'Meretöö seadus'})
  MS = Constant('MS', values={'long_name': 'Metsaseadus'})
  MTKS = Constant('MTKS', values={'long_name': 'Mikrolülituse topoloogia kaitse seadus'})
  MTUS = Constant('MTÜS', values={'long_name': 'Mittetulundusühingute seadus'})
  MuKS = Constant('MuKS', values={'long_name': 'Muinsuskaitseseadus'})
  MuuS = Constant('MuuS', values={'long_name': 'Muuseumiseadus'})
  MooteS = Constant('MõõteS', values={'long_name': 'Mõõteseadus'})
  MSVS = Constant('MSVS', values={'long_name': 'Märgukirjale ja selgitustaotlusele vastamise ning kollektiivse pöördumise esitamise seadus'})
  NETS = Constant('NETS', values={'long_name': 'Nakkushaiguste ennetamise ja tõrje seadus'})
  NPALS = Constant('NPALS', values={'long_name': 'Narkootiliste ja psühhotroopsete ainete ning nende lähteainete seadus'})
  NS = Constant('NS', values={'long_name': 'Nimeseadus'})
  NTS = Constant('NTS', values={'long_name': 'Noorsootöö seadus'})
  NotS = Constant('NotS', values={'long_name': 'Notariaadiseadus'})
  NotDVS = Constant('NotDVS', values={'long_name': 'Notari distsiplinaarvastutuse seadus'})
  NotTS = Constant('NotTS', values={'long_name': 'Notari tasu seadus'})
  OAS = Constant('OAS', values={'long_name': 'Ohvriabi seadus'})
  ReprS = Constant('ReprS', values={'long_name': 'Okupatsioonirežiimide poolt represseeritud isiku seadus'})
  PakAS = Constant('PakAS', values={'long_name': 'Pakendiaktsiisi seadus'})
  PakS = Constant('PakS', values={'long_name': 'Pakendiseadus'})
  PankrS = Constant('PankrS', values={'long_name': 'Pankrotiseadus'})
  PatS = Constant('PatS', values={'long_name': 'Patendiseadus'})
  PatVS = Constant('PatVS', values={'long_name': 'Patendivoliniku seadus'})
  PHS = Constant('PHS', values={'long_name': 'Perehüvitiste seadus'})
  PKS = Constant('PKS', values={'long_name': 'Perekonnaseadus'})
  PKTS = Constant('PKTS', values={'long_name': 'Perekonnaseisutoimingute seadus'})
  STS2004_2006 = Constant('STS2004_2006', values={'long_name': 'Perioodi 2004–2006 struktuuritoetuse seadus'})
  STS2007_2013 = Constant('STS2007_2013', values={'long_name': 'Perioodi 2007–2013 struktuuritoetuse seadus'})
  STS2014_2020 = Constant('STS2014_2020', values={'long_name': 'Perioodi 2014–2020 struktuuritoetuse seadus'})
  PlanS = Constant('PlanS', values={'long_name': 'Planeerimisseadus'})
  PPVS = Constant('PPVS', values={'long_name': 'Politsei ja piirivalve seadus'})
  PorTS = Constant('PorTS', values={'long_name': 'Pornograafilise sisuga ja vägivalda või julmust propageerivate teoste leviku reguleerimise seadus'})
  PostiS = Constant('PostiS', values={'long_name': 'Postiseadus'})
  ProkS = Constant('ProkS', values={'long_name': 'Prokuratuuriseadus'})
  PsAS = Constant('PsAS', values={'long_name': 'Psühhiaatrilise abi seadus'})
  PRS = Constant('PRS', values={'long_name': 'Punase risti nimetuse ja embleemi seadus'})
  PISTS = Constant('PISTS', values={'long_name': 'Puuetega inimeste sotsiaaltoetuste seadus'})
  PGS = Constant('PGS', values={'long_name': 'Põhikooli- ja gümnaasiumiseadus'})
  PSJKS = Constant('PSJKS', values={'long_name': 'Põhiseaduslikkuse järelevalve kohtumenetluse seadus'})
  PoLAS = Constant('PõLAS', values={'long_name': 'Põllumajandusloomade aretuse seadus'})
  PoRS = Constant('PõRS', values={'long_name': 'Põllumajandusreformi seadus'})
  ParS = Constant('PärS', values={'long_name': 'Pärimisseadus'})
  PaasteS = Constant('PäästeS', values={'long_name': 'Päästeseadus'})
  PaasteTS = Constant('PäästeTS', values={'long_name': 'Päästeteenistuse seadus'})
  PTS = Constant('PTS', values={'long_name': 'Pühade ja tähtpäevade seadus'})
  VSaarS = Constant('VSaarS', values={'long_name': 'Püsiasustusega väikesaarte seadus'})
  RPS = Constant('RPS', values={'long_name': 'Raamatupidamise seadus'})
  RahaPTS = Constant('RahaPTS', values={'long_name': 'Rahapesu ja terrorismi rahastamise tõkestamise seadus'})
  RaHS = Constant('RaHS', values={'long_name': 'Rahvahääletuse seadus'})
  RaRS = Constant('RaRS', values={'long_name': 'Rahvaraamatukogu seadus'})
  RRS = Constant('RRS', values={'long_name': 'Rahvastikuregistri seadus'})
  RTerS = Constant('RTerS', values={'long_name': 'Rahvatervise seadus'})
  ROS = Constant('ROS', values={'long_name': 'Rahvusooperi seadus'})
  REOS = Constant('REÕS', values={'long_name': 'Rahvusvahelise eraõiguse seadus'})
  RTsMS = Constant('RTsMS', values={'long_name': 'Rahvusvahelisel tsiviilmissioonil osalemise seadus'})
  RSanS = Constant('RSanS', values={'long_name': 'Rahvusvahelise sanktsiooni seadus'})
  RakKKS = Constant('RakKKS', values={'long_name': 'Rakenduskõrgkooli seadus'})
  RKESS = Constant('RKESS', values={'long_name': 'Rakkude, kudede ja elundite hankimise, käitlemise ja siirdamise seadus'})
  RKSS = Constant('RKSS', values={'long_name': 'Raseduse katkestamise ja steriliseerimise seadus'})
  RVMS = Constant('RVMS', values={'long_name': 'Raskeveokimaksu seadus'})
  RdtS = Constant('RdtS', values={'long_name': 'Raudteeseadus'})
  RaKS = Constant('RaKS', values={'long_name': 'Ravikindlustuse seadus'})
  RavS = Constant('RavS', values={'long_name': 'Ravimiseadus'})
  RekS = Constant('RekS', values={'long_name': 'Reklaamiseadus'})
  RelvS = Constant('RelvS', values={'long_name': 'Relvaseadus'})
  RES = Constant('RES', values={'long_name': 'Riigieelarve seadus'})
  RHS = Constant('RHS', values={'long_name': 'Riigihangete seadus'})
  RKSKS = Constant('RKSKS', values={'long_name': 'Riigikaitseliste sundkoormiste seadus'})
  RiKS = Constant('RiKS', values={'long_name': 'Riigikaitseseadus'})
  RKKTS = Constant('RKKTS', values={'long_name': 'Riigikogu kodu- ja töökorra seadus'})
  RKLS = Constant('RKLS', values={'long_name': 'Riigikogu liikme staatuse seadus'})
  RKVS = Constant('RKVS', values={'long_name': 'Riigikogu valimise seadus'})
  RKS = Constant('RKS', values={'long_name': 'Riigikontrolli seadus'})
  RKPSS = Constant('RKPSS', values={'long_name': 'Riigi kultuuripreemiate ja kultuuristipendiumide seadus'})
  RLS = Constant('RLS', values={'long_name': 'Riigilõivuseadus'})
  RiPS = Constant('RiPS', values={'long_name': 'Riigipiiri seadus'})
  RSVS = Constant('RSVS', values={'long_name': 'Riigisaladuse ja salastatud välisteabe seadus'})
  RTS = Constant('RTS', values={'long_name': 'Riigi Teataja seadus'})
  RVaS = Constant('RVaS', values={'long_name': 'Riigivapi seadus'})
  RVS = Constant('RVS', values={'long_name': 'Riigivaraseadus'})
  RVastS = Constant('RVastS', values={'long_name': 'Riigivastutuse seadus'})
  ROS = Constant('RÕS', values={'long_name': 'Riigi õigusabi seadus'})
  RERS = Constant('RERS', values={'long_name': 'Riiklike elatusrahade seadus'})
  RPTS = Constant('RPTS', values={'long_name': 'Riiklike peretoetuste seadus'})
  RMTS = Constant('RMTS', values={'long_name': 'Riikliku matusetoetuse seadus'})
  RPKS = Constant('RPKS', values={'long_name': 'Riikliku pensionikindlustuse seadus'})
  RStS = Constant('RStS', values={'long_name': 'Riikliku statistika seadus'})
  RAS = Constant('RAS', values={'long_name': 'Ruumiandmete seadus'})
  SadS = Constant('SadS', values={'long_name': 'Sadamaseadus'})
  SanS = Constant('SanS', values={'long_name': 'Saneerimisseadus'})
  SeOS = Constant('SeOS', values={'long_name': 'Seadme ohutuse seadus'})
  SVS = Constant('SVS', values={'long_name': 'Seadus süümevande andmise korra kohta'})
  SAS = Constant('SAS', values={'long_name': 'Sihtasutuste seadus'})
  SVPS = Constant('SVPS', values={'long_name': 'Soodustingimustel vanaduspensionide seadus'})
  SoVS = Constant('SoVS', values={'long_name': 'Soolise võrdõiguslikkuse seadus'})
  SHS = Constant('SHS', values={'long_name': 'Sotsiaalhoolekande seadus'})
  SMS = Constant('SMS', values={'long_name': 'Sotsiaalmaksuseadus'})
  SUS = Constant('SÜS', values={'long_name': 'Sotsiaalseadustiku üldosa seadus'})
  SpS = Constant('SpS', values={'long_name': 'Spordiseadus'})
  StrKS = Constant('StrKS', values={'long_name': 'Strateegilise kauba seadus'})
  SES = Constant('SES', values={'long_name': 'Sundeksemplari seadus'})
  SPTS = Constant('SPTS', values={'long_name': 'Surma põhjuse tuvastamise seadus'})
  SHKS = Constant('SHKS', values={'long_name': 'Sõjahaudade kaitse seadus'})
  SaES = Constant('SäES', values={'long_name': 'Säilituseksemplari seadus'})
  SaAS = Constant('SäAS', values={'long_name': 'Säästva arengu seadus'})
  SoS = Constant('SöS', values={'long_name': 'Söödaseadus'})
  SKHS = Constant('SKHS', values={'long_name': 'Süüteomenetluses tekitatud kahju hüvitamise seadus'})
  TFS = Constant('TFS', values={'long_name': 'Tagatisfondi seadus'})
  TPSKS = Constant('TPSKS', values={'long_name': 'Taimede paljundamise ja sordikaitse seadus'})
  TaimKS = Constant('TaimKS', values={'long_name': 'Taimekaitseseadus'})
  TTUKS = Constant('TTÜKS', values={'long_name': 'Tallinna Tehnikaülikooli seadus'})
  TKS = Constant('TKS', values={'long_name': 'Tarbijakaitseseadus'})
  TUKS = Constant('TÜKS', values={'long_name': 'Tartu Ülikooli seadus'})
  TAKS = Constant('TAKS', values={'long_name': 'Teadus- ja arendustegevuse korralduse seadus'})
  TeenMS = Constant('TeenMS', values={'long_name': 'Teenetemärkide seadus'})
  TTKS = Constant('TTKS', values={'long_name': 'Tervishoiuteenuste korraldamise seadus'})
  ToiduS = Constant('ToiduS', values={'long_name': 'Toiduseadus'})
  TS = Constant('TS', values={'long_name': 'Tolliseadus'})
  TNVS = Constant('TNVS', values={'long_name': 'Toote nõuetele vastavuse seadus'})
  TsMS = Constant('TsMS', values={'long_name': 'Tsiviilkohtumenetluse seadustik'})
  TsMSRS = Constant('TsMSRS', values={'long_name': 'Tsiviilkohtumenetluse seadustiku ja täitemenetluse seadustiku rakendamise seadus'})
  TsUS = Constant('TsÜS', values={'long_name': 'Tsiviilseadustiku üldosa seadus'})
  TubS = Constant('TubS', values={'long_name': 'Tubakaseadus'})
  TuOS = Constant('TuOS', values={'long_name': 'Tuleohutuse seadus'})
  TuMS = Constant('TuMS', values={'long_name': 'Tulumaksuseadus'})
  TUS = Constant('TÜS', values={'long_name': 'Tulundusühistuseadus'})
  TuKS = Constant('TuKS', values={'long_name': 'Tunnistajakaitse seadus'})
  TurS = Constant('TurS', values={'long_name': 'Turismiseadus'})
  TurvaS = Constant('TurvaS', values={'long_name': 'Turvaseadus'})
  ToS = Constant('TõS', values={'long_name': 'Tõestamisseadus'})
  TaKS = Constant('TäKS', values={'long_name': 'Täiskasvanute koolituse seadus'})
  TMS = Constant('TMS', values={'long_name': 'Täitemenetluse seadustik'})
  TLS = Constant('TLS', values={'long_name': 'Töölepingu seadus'})
  TDKS = Constant('TDKS', values={'long_name': 'Tööstusdisaini kaitse seadus'})
  THS = Constant('THS', values={'long_name': 'Tööstusheite seadus'})
  TOAS = Constant('TÕAS', values={'long_name': 'Tööstusomandi õiguskorralduse aluste seadus'})
  TDVS = Constant('TDVS', values={'long_name': 'Töötajate distsiplinaarvastutuse seadus'})
  TUIS = Constant('TUIS', values={'long_name': 'Töötajate usaldusisiku seadus'})
  TUUKS = Constant('TÜÜKS', values={'long_name': 'Töötajate üleühenduselise kaasamise seadus'})
  TTOS = Constant('TTOS', values={'long_name': 'Töötervishoiu ja tööohutuse seadus'})
  TTTS = Constant('TTTS', values={'long_name': 'Tööturuteenuste ja -toetuste seadus'})
  TKindlS = Constant('TKindlS', values={'long_name': 'Töötuskindlustuse seadus'})
  TVTS = Constant('TVTS', values={'long_name': 'Töövõimetoetuse seadus'})
  VPVS = Constant('VPVS', values={'long_name': 'Vabariigi Presidendi valimise seadus'})
  VVR = Constant('VVR', values={'long_name': 'Vabariigi Valitsuse reglement'})
  VVS = Constant('VVS', values={'long_name': 'Vabariigi Valitsuse seadus'})
  VTS = Constant('VTS', values={'long_name': 'Vandetõlgi seadus'})
  VHS = Constant('VHS', values={'long_name': 'Vanemahüvitise seadus'})
  VangS = Constant('VangS', values={'long_name': 'Vangistusseadus'})
  VKEMS = Constant('VKEMS', values={'long_name': 'Vedelkütuse erimärgistamise seadus'})
  VKS = Constant('VKS', values={'long_name': 'Vedelkütuse seadus'})
  VKVS = Constant('VKVS', values={'long_name': 'Vedelkütusevaru seadus'})
  VeeS = Constant('VeeS', values={'long_name': 'Veeseadus'})
  VereS = Constant('VereS', values={'long_name': 'Vereseadus'})
  VetKS = Constant('VetKS', values={'long_name': 'Veterinaarkorralduse seadus'})
  VOS = Constant('VÕS', values={'long_name': 'Võlaõigusseadus'})
  VOSRS = Constant('VÕSRS', values={'long_name': 'Võlaõigusseaduse, tsiviilseadustiku üldosa seaduse ja rahvusvahelise eraõiguse seaduse rakendamiseseadus'})
  VOVS = Constant('VÕVS', values={'long_name': 'Võlgade ümberkujundamise ja võlakaitse seadus'})
  VordKS = Constant('VõrdKS', values={'long_name': 'Võrdse kohtlemise seadus'})
  VaetS = Constant('VäetS', values={'long_name': 'Väetiseseadus'})
  VRKAS = Constant('VRKAS', values={'long_name': 'Vähemusrahvuse kultuuriautonoomia seadus'})
  VRKS = Constant('VRKS', values={'long_name': 'Välismaalasele rahvusvahelise kaitse andmise seadus'})
  VMS = Constant('VMS', values={'long_name': 'Välismaalaste seadus'})
  VKTS = Constant('VKTS', values={'long_name': 'Välisriigi kutsekvalifikatsiooni tunnustamise seadus'})
  VaSS = Constant('VäSS', values={'long_name': 'Välissuhtlemisseadus'})
  VaTS = Constant('VäTS', values={'long_name': 'Välisteenistuse seadus'})
  VOKS = Constant('VÕKS', values={'long_name': 'Välisõhu kaitse seadus'})
  VSS = Constant('VSS', values={'long_name': 'Väljasõidukohustuse ja sissesõidukeelu seadus'})
  VAPS = Constant('VAPS', values={'long_name': 'Väljateenitud aastate pensionide seadus'})
  VMTS = Constant('VMTS', values={'long_name': 'Väärismetalltoodete seadus'})
  VTMS = Constant('VTMS', values={'long_name': 'Väärteomenetluse seadustik'})
  VPTS = Constant('VPTS', values={'long_name': 'Väärtpaberituru seadus'})
  OKS = Constant('ÕKS', values={'long_name': 'Õiguskantsleri seadus'})
  OVVS = Constant('ÕVVS', values={'long_name': 'Õigusvastaselt võõrandatud vara maksumuse määramise ja kompenseerimise seadus'})
  OOS = Constant('ÕÕS', values={'long_name': 'Õppetoetuste ja õppelaenu seadus'})
  AS = Constant('ÄS', values={'long_name': 'Äriseadustik'})
  UTS = Constant('ÜTS', values={'long_name': 'Ühistranspordiseadus'})
  UVVKS = Constant('ÜVVKS', values={'long_name': 'Ühisveevärgi ja -kanalisatsiooni seadus'})
  ULTS = Constant('ÜLTS', values={'long_name': 'Üleliigse laovaru tasu seadus'})
  UKS = Constant('ÜKS', values={'long_name': 'Ülikooliseadus'})
  UVLS = Constant('ÜVLS', values={'long_name': 'Üürivaidluse lahendamise seadus'})


class Categories(ConstantMixin):
  EESTI = Constant('Eesti', [
    Constant('Eesti kohtulahendid', [
      Constant('Riigiteataja kohtuuudised', values={'link': 'https://www.riigiteataja.ee/oigusuudised/kohtuuudiste_nimekiri.html',
                                                    'lang': 'eesti', 'search_function': riigiteataja_parse.search_riigiteataja_uudised}),
      Constant('Hiljutised Riigikohtu lahendid', values={'link': 'http://www.nc.ee', 'lang': 'eesti',
                                                         'search_function': rss_parse.parse_feed, 'rss_sources': ['http://www.nc.ee/rss/?lahendid=1&tyyp=K']}),
      Constant('Riigikohtu lahendite arhiiv', values={'link': 'http://www.nc.ee', 'lang': 'eesti'}),
      Constant('Maa- ja ringkonnakohtu lahendid', values={'link': 'https://www.riigiteataja.ee/kohtuteave/maa_ringkonna_kohtulahendid/otsi.html', 'lang': 'eesti',
                                                          'search_function': riigiteataja_parse.search_kohtu})
    ]),
    Constant('Ministeeriumid', [
      Constant('Kaitseministeerium', values={'link': 'http://www.kaitseministeerium.ee', 'lang': 'eesti',
                                             'search_function': rss_parse.parse_feed, 'rss_sources': ['http://www.kaitseministeerium.ee/et/rss-uudiste-voog']}),
      Constant('Finantsministeerium', values={'link': 'http://www.fin.ee', 'lang': 'eesti',
                                              'search_function': rss_parse.parse_feed, 'rss_sources': ['http://www.fin.ee/rss_uudised']}),
      Constant('Justiitsministeerium', values={'link': 'http://www.just.ee', 'lang': 'eesti',
                                               'search_function': ministry_parse.search_ministry}),
      Constant('Keskkonnaministeerium', values={'link': 'http://www.envir.ee', 'lang': 'eesti',
                                                'search_function': ministry_parse.search_ministry}),
      Constant('Kultuuriministeerium', values={'link': 'http://www.kul.ee', 'lang': 'eesti',
                                               'search_function': ministry_parse.search_ministry}),
      Constant('Põllumajandusministeerium', values={'link': 'http://www.agri.ee', 'lang': 'eesti',
                                                    'search_function': ministry_parse.search_ministry}),
      Constant('Siseministeerium', values={'link': 'https://www.siseministeerium.ee', 'lang': 'eesti',
                                           'search_function': ministry_parse.search_ministry}),
      Constant('Sotsiaalministeerium', values={'link': 'http://www.sm.ee', 'lang': 'eesti',
                                               'search_function': ministry_parse.search_ministry}),
      Constant('Välisministeerium', values={'link': 'http://vm.ee', 'lang': 'eesti',
                                            'search_function': ministry_parse.search_ministry}),
      Constant('Riigikogu pressiteated', values={'link': 'http://www.riigikogu.ee/index.php?id=31549', 'lang': 'eesti',
                                                 'search_function': rss_parse.parse_feed, 'rss_sources': ['http://feeds.feedburner.com/RiigikoguPressiteated?format=xml']})
    ]),
    Constant('Õigusaktid ja eelnõud', [
      Constant('Kooskõlastamiseks esitatud eelnõud', values={'link': 'http://eelnoud.valitsus.ee/main#SKixD73F', 'lang': 'eesti',
                                                             'search_function': rss_parse.parse_feed, 'rss_sources': ['http://eelnoud.valitsus.ee/main/mount/rss/home/review.rss']}),
      Constant('Valitsusele esitatud eelnõud', values={'link': 'http://eelnoud.valitsus.ee/main#SKixD73F', 'lang': 'eesti',
                                                       'search_function': rss_parse.parse_feed, 'rss_sources': ['http://eelnoud.valitsus.ee/main/mount/rss/home/submission.rss']}),
      Constant('Riigiteataja ilmumas/ilmunud seadused', values={'link': 'https://www.riigiteataja.ee/', 'lang': 'eesti'}),
      Constant('Õigusaktide otsing', values={'link': 'https://www.riigiteataja.ee/', 'lang': 'eesti',
                                             'search_function': riigiteataja_parse.search_oigusaktid}),
      Constant('Riigiteataja seadused', values={'link': 'https://www.riigiteataja.ee/', 'lang': 'eesti',
                                                'search_function': riigiteataja_parse.search_seadused})
    ]),
    Constant('Euroopa õigus', [
      Constant('Eur-Lex kohtuasjade rss', values={'link': 'http://eur-lex.europa.eu', 'lang': 'eesti',
                                                  'search_function': rss_parse.parse_feed, 'rss_sources': ['http://eur-lex.europa.eu/ET/display-feed.rss?rssId=163']}), # NB! siin on võimalik keelt muuta\
      Constant('Eur-Lex Komisjoni ettepanekute rss', values={'link': 'http://eur-lex.europa.eu', 'lang': 'eesti',
                                                             'search_function': rss_parse.parse_feed, 'rss_sources': ['http://eur-lex.europa.eu/ET/display-feed.rss?rssId=161']}),
      Constant('Eur-Lex Parlamendi ja Nõukogu rss', values={'link': 'http://eur-lex.europa.eu', 'lang': 'eesti',
                                                            'search_function': rss_parse.parse_feed, 'rss_sources': ['http://eur-lex.europa.eu/ET/display-feed.rss?rssId=162']}),
      Constant('Eur-Lex eestikeelsete dokumentide otsing', values={'link': 'http://eur-lex.europa.eu/advanced-search-form.html', 'lang': 'eesti',
                                                                   'search_function': eurlex_parse.search_eurlex})
    ]),
    Constant('Uudised ja foorumid', [
      Constant('ERR', values={'link': 'http://www.err.ee', 'lang': 'eesti',
                              'search_function': rss_parse.parse_feed, 'rss_sources': ['http://www.err.ee/rss']}),
      Constant('Delfi', values={'link': 'http://www.delfi.ee', 'lang': 'eesti',
                                'search_function': rss_parse.parse_feed, 'rss_sources': [
                                  'http://feeds2.feedburner.com/delfiuudised?format=xml',
                                  'http://feeds.feedburner.com/delfimaailm?format=xml',
                                  'http://feeds.feedburner.com/delfi110-112?format=xml',
                                  'http://feeds2.feedburner.com/delfimajandus'
                                ]}),
      Constant('Postimees', values={'link': 'http://www.postimees.ee', 'lang': 'eesti',
                                    'search_function': rss_parse.parse_feed, 'rss_sources': [
                                      'http://majandus24.postimees.ee/rss',
                                      'http://www.postimees.ee/rss/',
                                      'http://www.postimees.ee/rss/?r=128'
        ]}),
      Constant('Õhtuleht', values={'link': 'http://www.ohtuleht.ee', 'lang': 'eesti',
                                   'search_function': rss_parse.parse_feed, 'rss_sources': ['http://www.ohtuleht.ee/rss']}),
      Constant('Päevaleht', values={'link': 'http://epl.delfi.ee/', 'lang': 'eesti',
                                    'search_function': rss_parse.parse_feed, 'rss_sources': ['http://feeds.feedburner.com/eestipaevaleht?format=xml']}),
      Constant('Eesti Ekspress', values={'link': 'http://ekspress.delfi.ee/', 'lang': 'eesti',
                                         'search_function': rss_parse.parse_feed, 'rss_sources': ['http://feeds.feedburner.com/EestiEkspressFeed?format=xml']}),
      Constant('Maaleht', values={'link': 'http://maaleht.delfi.ee/', 'lang': 'eesti',
                                  'search_function': rss_parse.parse_feed, 'rss_sources': ['http://feeds.feedburner.com/maaleht?format=xml']}),
      Constant('Äripäev', values={'link': 'http://www.aripaev.ee', 'lang': 'eesti',
                                  'search_function': rss_parse.parse_feed, 'rss_sources': ['http://www.aripaev.ee/rss']}),
      Constant('raamatupidaja.ee', values={'link': 'http://www.raamatupidaja.ee/', 'lang': 'eesti',
                                           'search_function': rss_parse.parse_feed, 'rss_sources': ['http://raamatupidaja.ee/RSS.aspx']}),
      Constant('juura.ee', values={'link': 'http://juura.ee', 'lang': 'eesti',
                                   'search_function': rss_parse.parse_feed, 'rss_sources': ['http://juura.ee/gw.php/news/aggregate/index/format/xml']}),
      Constant('Riigiteataja seadusuudised', values={'link': 'https://www.riigiteataja.ee/oigusuudised/seadusteUudisteNimekiri.html',
                                                     'lang': 'eesti', 'search_function': riigiteataja_parse.search_riigiteataja_uudised}),
      Constant('Riigiteataja õigusuudised', values={'link': 'https://www.riigiteataja.ee/oigusuudised/muuOigusuudisteNimekiri.html',
                                                    'lang': 'eesti', 'search_function': riigiteataja_parse.search_riigiteataja_uudised}),
      Constant('Riigikohtu uudised', values={'link': 'http://www.nc.ee', 'lang': 'eesti',
                                             'search_function': rss_parse.parse_feed, 'rss_sources': ['http://www.nc.ee/rss/?uudised=1']})
    ])
  ])
  ARHIIVID = Constant('Arhiivid')
  SANKTSIOONID = Constant('Sanktsioonid')
  KOHTUREGISTRID = Constant('Kohturegistrid')
