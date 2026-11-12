"""Exercise deployment routing without installing or invoking the engine."""
import json,shutil,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class IngestionWrappers(unittest.TestCase):
    def check_wrapper(self,shell,extension,stub):
        if not shell:self.skipTest('Required shell unavailable')
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);scripts=root/'scripts';scripts.mkdir()
            for name in ('ingest','ingest-tex'):
                shutil.copyfile(ROOT/'scripts'/f'{name}.{extension}',scripts/f'{name}.{extension}')
            (scripts/f'run-engine.{extension}').write_text(stub,encoding='utf-8')
            def run(name,args):
                command=([shell,'-NoProfile','-File'] if extension=='ps1' else [shell])+[str(scripts/f'{name}.{extension}'),*args]
                return subprocess.run(command,capture_output=True,text=True,timeout=20)
            for name,args,product in [('ingest',[],'words'),('ingest',['words'],'words'),('ingest',['tex'],'tex'),('ingest-tex',[],'tex')]:
                with self.subTest(name=name,args=args):
                    result=run(name,args+['--source-kind','docs'])
                    self.assertEqual(result.returncode,0,result.stderr)
                    values=json.loads(result.stdout) if extension=='ps1' else result.stdout.splitlines()
                    self.assertIn('aspose.'+product+'.cpp',values)
                    expected_root = subprocess.check_output([shell, '-c', 'pwd'], cwd=root, text=True).strip() if extension == 'sh' else str(root).replace('\\', '/')
                    self.assertEqual(values[values.index('--workspace') + 1].replace('\\', '/'), expected_root + '/engine')
                    self.assertIn('--source-kind',values)
            for name in ('ingest','ingest-tex'):
                for args in (['--workspace','elsewhere'],['--catalog=other.json'],['--python','other-python']):
                    with self.subTest(name=name,args=args):
                        result=run(name,args)
                        self.assertNotEqual(result.returncode,0)
                        self.assertNotIn('aspose.',result.stdout)
    def test_shell_routing_and_overrides(self):
        self.check_wrapper(shutil.which('sh'),'sh',"#!/bin/sh\nprintf '%s\\n' \"$@\"\n")
    def test_powershell_routing_and_overrides(self):
        self.check_wrapper(shutil.which('pwsh') or shutil.which('powershell'),'ps1','$args | ConvertTo-Json -Compress\nexit 0\n')
if __name__=='__main__':unittest.main()
